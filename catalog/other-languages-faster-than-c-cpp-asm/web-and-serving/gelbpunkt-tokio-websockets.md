# tokio-websockets

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Strict RFC 6455 WebSocket client/server crate for Tokio; ties or edges mongoose (C) on HttpArena small-message echo.

| | |
|---|---|
| **Beats** | mongoose (C, gcc-14 -O3 -march=native -flto, OpenSSL backend, epoll, one mg_mgr per core) and ringzero-ws (C, io_uring); proxygen (C++) rows in the same HttpArena suite |
| **Claimed result** | echo-ws-limited-4096: 2,641,801 msg/s vs mongoose 2,533,448 (1.04x), proxygen 1,063,324 (2.48x); echo-ws-limited-512: 2,171,052 vs mongoose 2,123,165 (1.02x), proxygen 981,328 (2.21x); ringzero-ws does not run the limited profiles. echo-ws-512: 4,194,604 vs mongoose 3,954,919 (1.06x), proxygen 3,179,995 (1.32x), but ringzero-ws (C, io_uring) 4,353,147 (0.96x); echo-ws-4096: 4,198,339 vs mongoose 4,022,433 (1.04x), ringzero-ws 4,429,548 (0.95x); echo-ws-16384: 3,956,026 vs mongoose 3,838,015 (1.03x), ringzero-ws 4,066,852 (0.97x). Pipelined rows lose: echo-ws-pipeline-4096 20,757,419 vs mongoose 59,017,072 (0.35x), ringzero-ws 68,438,198 (0.30x), proxygen 49,666,723 (0.42x). All ratios derived from page data. |
| **Workload** | HttpArena WebSocket echo profiles (gcannon, plaintext, small messages: about 6.7 bytes of server output per echoed message, derived from page data) for a tokio-websockets 0.13 echo server written for the suite: one current_thread Tokio runtime per available CPU (64), each with its own SO_REUSEPORT listener, tokio::spawn per connection, unlimited frame size and limits (frameworks/tokio-websockets/src/main.rs; not the multi-threaded runtime). Profiles: echo-ws at 512, 4096 and 16384 connections; echo-ws-limited at 512 and 4096 (short-lived connections closed after 10 messages, not a rate limit); echo-ws-pipeline (16 messages in flight per connection) at 512, 4096 and 16384. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (64 cores / 128 threads), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json, undated, describes the machine now). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) and the load generator (gcannon for HTTP/1.1 and WebSocket, wrk for json-tls and static-tls) runs on CPUs 32-63,96-127 of the same machine over loopback (scripts/lib/profiles.sh, scripts/lib/common.sh); each row is the best of 3 runs of 5 s against one container (scripts/benchmark.sh, RUNS=3). |
| **Compiler and flags** | tokio-websockets entry: rust:1.95 image switched to nightly-2026-06-27, RUSTFLAGS='-C target-cpu=native', opt-level 3, lto thin, codegen-units 1, panic abort; tokio-websockets 0.13 with features sha1_smol, server and nightly (the nightly feature only adds SIMD paths on non-x86 targets; x86_64 AVX2 masking and UTF-8 validation work on stable) (frameworks/tokio-websockets/Dockerfile and Cargo.toml). mongoose 7.23: gcc-14 -O3 -march=native -flto -std=gnu11, epoll, OpenSSL backend (unused on plaintext echo). ringzero-ws: gcc -O3 -march=native -pthread with liburing 2.9. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | yes |
| **Adoption** | 152 stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/Gelbpunkt/tokio-websockets) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio-websockets.json) |

## Verdict

In HttpArena (Threadripper PRO 3995WX, server pinned to 64 threads, gcannon client on the other 64 over loopback, best of 3 x 5 s), a contributed tokio-websockets 0.13 echo server built with nightly Rust, -C target-cpu=native and thin LTO echoed 2.17-4.20M small messages/s, 2-6 percent above the mongoose 7.23 C server (gcc-14 -O3 -march=native -flto) and well above proxygen, but 3-5 percent below the C io_uring ringzero-ws and at 0.30-0.42x of all three when 16 messages are pipelined.

## Use it when

- A Tokio service that needs a WebSocket server or client with strict RFC 6455 behaviour (UTF-8 and close-handshake validation, passes Autobahn without relaxations) and no permessage-deflate.
- Many small concurrent connections where per-connection memory matters: 36 MiB at 512 connections and 98 MiB at 4,096 in HttpArena, below mongoose's 51 and 179 MiB.
- Large binary or text payloads (16 KiB and up), where its SIMD masking and validation pay off; the project's own charts show it ahead of uWebSockets at 16 KiB (about 179k vs 120k msg/s at 10 connections, chart reading, first-party).
- Projects already depending on bytes, tokio-util and http, or that want to bring their own TLS (rustls, native-tls, or none) and SHA-1 backend (ring, aws-lc-rs, openssl, sha1_smol).
- Mature dependency choice: about 16.5 million crates.io downloads (7.6 million in the last 90 days) and 34 reverse dependencies including async-nats, iroh-relay, twilight-gateway and songbird.

## Skip it when

- You need permessage-deflate compression: the README lists it as unsupported.
- Pipelined or burst traffic with the naive send-per-message loop: HttpArena's echo-ws-pipeline rows run at 0.30-0.42x of ringzero-ws, mongoose and proxygen (20.8M vs 59.0-68.4M msg/s at 4,096 connections), because SinkExt::send flushes every frame.
- Lowest small-message latency per core is the goal: the hand-written C io_uring server ringzero-ws is 3-5 percent ahead on every non-pipelined row, and the project's own charts show uWebSockets ahead at 0- and 20-byte payloads (about 319k vs 290k msg/s).
- Sharing one stream between a reader task and a writer task through StreamExt::split: the maintainers call it an anti-pattern and issue #128 (poll_close can hang after a completed close handshake) is open.
- A non-Tokio runtime (async-std, glommio, monoio): it is built on tokio and tokio-util.

## How it is fast

Frame (un)masking dispatches at runtime (is_x86_feature_detected) to AVX-512, AVX2 or SSE2 kernels on x86-64 and NEON on aarch64, with more targets behind the nightly feature, and UTF-8 validation of text frames uses simdutf8. Payloads are Bytes, so echoing a message re-sends the same buffer without a copy, and since 0.12.0 queued frames are written with a single vectored write when the caller uses SinkExt::feed. In the HttpArena rows the messages are about 5-7 bytes, so none of the SIMD work matters there; the measured rows are dominated by one read and one write syscall per message (about 14.8 us of server CPU per echoed message at echo-ws-512 versus 16.4 us for mongoose and 14.2 us for ringzero-ws, derived from page data).

## Compared with alternatives

Among the catalogued web-and-serving entries it is the only WebSocket library; pick it over the raw Tokio or minima-sync HttpArena entries when you need a reusable, standards-strict WebSocket layer rather than a hand-written HTTP responder, and over wtx (wave 5) when you want the more widely used crate with strict compliance and pluggable TLS.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio, tokio-util, bytes, futures-core, futures-sink, simdutf8; one SHA-1 backend (sha1_smol, ring, aws-lc-rs or openssl) for client or server; base64, http, httparse for client/server; optional tokio-rustls or tokio-native-tls and an RNG crate (fastrand, getrandom or rand) for the client |
| **Minimum toolchain** | Rust 1.89 (MSRV, edition 2024); the nightly feature needs a nightly compiler |
| **Platforms** | any Tokio target; SIMD masking on x86-64 (SSE2, AVX2, AVX-512, runtime-detected) and aarch64 NEON on stable, plus 32-bit ARM, PowerPC, s390x and LoongArch with the nightly feature; SIMD UTF-8 validation on x86-64 AVX2 and aarch64 only |
| **Thread safety** | WebSocketStream is owned by one task; the implementation stores a single read waker and a single flush waker, and the maintainers advise against sharing it via StreamExt::split (issue #128, open). |
| **Drop-in for the baseline** | partial — protocol-compatible with any RFC 6455 peer, so it can replace a mongoose or uWebSockets server process, but it is a Rust/Tokio API, not a C or C++ library |

## Gotchas

- Harness flaw against the library: the HttpArena server (frameworks/tokio-websockets/src/main.rs, contributed by the wtx author) echoes with ws_stream.send(msg), which flushes one frame per write; the crate has batched queued frames into one vectored write since 0.12.0 when SinkExt::feed is used, so the 0.30-0.42x pipelined rows reflect the bench code, not a ceiling of the library.
- The headline 2-6 percent wins over mongoose compare files written in separate runs weeks apart (tokio-websockets.json 2026-08-28, mongoose.json 2026-09-21), every server uses 53-66 of its 64 pinned hardware threads, and messages are about 5-7 bytes, so the rows measure syscall and event-loop cost rather than WebSocket framing; treat them as a tie.
- The HttpArena server also sets Limits::unlimited() and unwraps send errors under panic = "abort", so one peer reset during an echo would abort the whole 64-runtime process; the crate defaults (64 MiB max payload, 4 MiB frame size, 8 KiB flush threshold) are the safer starting point.
- Message::close, Message::ping and Message::pong panic on reserved close codes or payloads over 123/125 bytes (since 0.11.0); validate user-supplied values before constructing them.

## Known shortcomings

- Beats mongoose by only 2-6% in cross-run rows (files written 2026-08-28 vs 2026-09-21); ringzero-ws (C) is ahead on every unlimited row and pipelined is 0.30-0.42x; its own charts show uWebSockets ahead at small payloads; the entry runs one current_thread runtime per core; echo-ws-limited closes connections after 10 messages rather than rate-limiting; best of 3 runs; 152 stars.
- Harness flaw that works against the library: the HttpArena server (written by the wtx author) echoes with ws_stream.send(msg), one flush per frame, while the crate has batched queued frames into one vectored write via SinkExt::feed since 0.12.0, so the 0.30-0.42x pipelined rows reflect the bench code, not the library. Non-pipelined rows use about 5-7-byte messages with servers busy on 53-66 of 64 threads, syscall-bound (14.8 us CPU per message vs mongoose 16.4 and ringzero-ws 14.2, derived); the 2-6% margin over mongoose is cross-run and effectively a tie. The bench server unwraps send errors under panic = "abort"; issue #128 (poll_close hang with split) is open; no permessage-deflate.

## Caveats and trade-offs

The margin over mongoose is 2 to 6 percent on the non-pipelined rows, and the hand-written C io_uring server ringzero-ws is 3 to 5 percent ahead on every unlimited row and 3.3x ahead on the pipelined rows; mongoose (an embedded general networking library) and proxygen are the only other C/C++ WebSocket entries, and uWebSockets is absent from the suite. Rows are best of 3 runs of 5 s against one container, but come from separate runs months apart: tokio-websockets.json was written 2026-08-28 (#1356), mongoose.json 2026-09-21 (#1489) and ringzero-ws.json no later than 2026-07-24 (per git history), so the 2 to 6 percent margins are cross-run comparisons. The entry was contributed by the author of the Rust wtx library (c410-f3r), not by the tokio-websockets authors; it echoes each message with SinkExt::send, which flushes per frame, which likely explains much of the 3x pipelined deficit. Messages are tiny (about 6.7 bytes of server output per message, derived from page data), so the library's SIMD masking and UTF-8 validation hardly matter here. The project's own benches/README.md (first-party, single-threaded runtime, Ryzen 9 7950X, uWebSockets HEAD built by its default build at -O3 -march=native with clang, load_test client; harness in benches/Dockerfile and run.py) shows chart images only: read approximately from the charts, uWebSockets leads at small payloads (100 connections 0 B about 319k vs 290k msg/s, 100 x 20 B about 318k vs 286k, 10 x 1 KiB about 296k vs 272k) and tokio-websockets leads at 16 KiB payloads (10 connections about 179k vs 120k, 200 about 173k vs 121k, 500 about 164k vs 119k). [retier] The HttpArena server (contributed by the wtx author) echoes with ws_stream.send(msg), one flush per frame, while the crate batches queued frames into one vectored write via SinkExt::feed since 0.12.0, so the 0.30-0.42x pipelined rows reflect the bench code. Non-pipelined rows use about 5-7-byte messages with servers busy on 53-66 of 64 threads, syscall-bound (14.8 us CPU per message vs mongoose 16.4 and ringzero-ws 14.2); the 2-6% margin over mongoose is cross-run and effectively a tie. Issue #128 (poll_close hang with split) is open; no permessage-deflate.

Strict RFC 6455 compliance (UTF-8 and close handshake validation), which the repo's own benches README contrasts with non-strict libraries; the HttpArena build enables the crate's nightly feature.

## Maintenance

Actively maintained (0.13.3 on crates.io 2026-06-25, last commit 2026-07-31), MIT-licensed, 152 stars but about 16.5 million downloads; copyable as a crate dependency, with three open issues including the split/poll_close hang (#128).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/tokio-websockets.json and the sibling mongoose, ringzero-ws and proxygen JSON files in MDA2AV/HttpArena; the code is public (frameworks/tokio-websockets/{Dockerfile,Cargo.toml,src/main.rs}, frameworks/mongoose/Dockerfile, frameworks/ringzero-ws/Dockerfile, scripts/benchmark.sh, scripts/lib/profiles.sh), flags are in the Dockerfiles and Cargo.toml, and the CPU (Threadripper PRO 3995WX) is in site/data/current.json, the HttpArena tier-A precedent.
- **Verifier notes:** All numbers verified; tier A on the HttpArena precedent. Corrections: the entry runs one current_thread runtime per core, not the multi-threaded runtime; echo-ws-limited means connections closed after 10 messages, not rate limiting; added echo-ws-16384 and proxygen ratios. Shortcomings to record: 2-6 percent cross-run margin over mongoose only; ringzero-ws (C) ahead on all unlimited rows and 3.3x on pipelined; pipelined 0.30x-0.42x of the C/C++ entries; uWebSockets absent from the suite and ahead at small payloads in the project's own charts; 152 stars.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-101 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio-websockets.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ringzero-ws.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ringzero-ws/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ringzero-ws/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/tokio-websockets.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/tokio-websockets>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/mongoose.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/ringzero-ws.json>
  - <https://github.com/MDA2AV/HttpArena/pull/1356>
  - <https://github.com/Gelbpunkt/tokio-websockets>
  - <https://github.com/Gelbpunkt/tokio-websockets/commits>
  - <https://github.com/Gelbpunkt/tokio-websockets/tree/main/benches>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/Dockerfile>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/run.py>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/README.md>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/results/x86_64-avx2/100-0-chart.png>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/results/x86_64-avx2/100-20-chart.png>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/results/x86_64-avx2/10-1024-chart.png>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/results/x86_64-avx2/10-16384-chart.png>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/results/x86_64-avx2/200-16384-chart.png>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/results/x86_64-avx2/500-16384-chart.png>
  - <https://raw.githubusercontent.com/uNetworking/uWebSockets/HEAD/build.c>
- **Sources the enricher read:**
  - <https://github.com/Gelbpunkt/tokio-websockets>
  - <https://github.com/Gelbpunkt/tokio-websockets/issues?q=is%3Aissue>
  - <https://github.com/Gelbpunkt/tokio-websockets/issues/128>
  - <https://github.com/Gelbpunkt/tokio-websockets/issues/116>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/README.md>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/mask.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/utf8.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/server.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/proto/stream.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/proto/types.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/proto/codec.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/src/proto/mod.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/examples/echo_server.rs>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/Dockerfile>
  - <https://raw.githubusercontent.com/Gelbpunkt/tokio-websockets/HEAD/benches/run.py>
  - <https://crates.io/api/v1/crates/tokio-websockets>
  - <https://crates.io/api/v1/crates/tokio-websockets/reverse_dependencies?per_page=10>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-websockets/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio-websockets.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ringzero-ws.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/tools/gcannon.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/gelbpunkt/tokio-websockets`) · [data/wave14/enrich/raw/github_com_gelbpunkt_tokio_websockets.json](../../../data/wave14/enrich/raw/github_com_gelbpunkt_tokio_websockets.json) (enrichment confidence 0.75)

</details>
