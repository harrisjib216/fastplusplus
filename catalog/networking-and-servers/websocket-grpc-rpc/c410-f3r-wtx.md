# wtx (gRPC server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Rust crate with its own HTTP/2 and gRPC stack. Its unary gRPC server served 3.7-5.5x grpc-go's req/s on HttpArena.

| | |
|---|---|
| **Beats** | gRPC (grpc-go, official google.golang.org/grpc implementation) |
| **Claimed result** | 3.7-5.5x higher req/s than grpc-go: 3,990,708 vs 720,798 rps at 256 conns (avg latency 6.55ms vs 35.14ms); 3,620,970 vs 969,718 rps at 1024 conns (avg latency 26.89ms vs 88.65ms) (derived from page data) |
| **Workload** | Unary gRPC GetSum call (9-byte protobuf request) over plaintext HTTP/2 (h2c), h2load load generator with 256 and 1024 connections and 100 concurrent streams per connection, 5s duration, 3 runs with the best taken, on the HttpArena multi-language benchmark harness. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, single NUMA node, performance governor). Per HttpArena's Hardware & Topology docs, the server is pinned to a 64-thread cpuset (0-31,64-95 = 32 physical cores plus SMT siblings) and the load generator to the other half of the same chip; every run uses the same machine. |
| **Compiler and flags** | wtx: Rust nightly-2026-06-27 (rust:1.95 base image), `RUSTFLAGS="-C target-cpu=native" cargo build --release` with release profile opt-level=3, lto="thin", codegen-units=1, panic="abort"; wtx 0.49 (features grpc-server, optimizations-std, quick-protobuf, tokio) per frameworks/wtx-grpc/Dockerfile and Cargo.toml in MDA2AV/HttpArena. grpc-go: Go 1.24 (golang:1.24-bookworm image), `CGO_ENABLED=0 go build`, google.golang.org/grpc v1.72.0, default grpc.NewServer() with GOMAXPROCS=NumCPU (frameworks/grpc-go). |
| **Adoption** | 401 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/c410-f3r/wtx) · [benchmark](https://www.http-arena.com/data.json) |

## Verdict

HttpArena ran a unary GetSum gRPC call over plaintext h2c, driven by h2load with 256 and 1024 connections, 100 streams each, 5 s runs, best of 3. The machine was a Threadripper PRO 3995WX, with the server pinned to 32 cores plus their SMT threads. wtx 0.49 (nightly Rust, target-cpu=native) served 3,990,708 req/s against grpc-go v1.72.0 (Go 1.24, default grpc.NewServer) at 720,798 req/s with 256 connections (5.5x). With 1024 connections it served 3,620,970 against 969,718 (3.7x). Two limits apply: wtx used about 64 logical CPUs against grpc-go's 44, and the two results come from different run dates (grpc-go on 2026-04-12, wtx re-validated on 2026-08-24).

## Use it when

- A Rust service whose hot path is small unary gRPC calls at very high request rates on a many-core Linux box. On HttpArena, wtx served 3.99M req/s against grpc-go's 0.72M with 256 h2c connections.
- Workloads with hundreds to thousands of connections, each carrying many concurrent streams. These spread well across the per-thread listeners; the benchmark used 256-1024 connections with 100 streams each.
- gRPC over TLS without a separate TLS stack: in HttpArena's unary-grpc-tls test, with wtx's own TLS 1.3, it reached 3.69M vs 0.70M req/s (256 connections) and 3.63M vs 0.93M (1024).
- Internal services, prototypes or benchmark rigs where you control the .proto files and both ends, and you can type the service routes by hand.
- Projects that want gRPC, HTTP/2, WebSocket and Postgres from one crate with a small dependency tree and fast builds. The README reports 2 required dependencies and a 6.53 s clean optimized build for the gRPC client.

## Skip it when

- You need server, client or bidirectional streaming RPCs. The gRPC module supports unary calls only.
- You need generated service stubs or the usual gRPC ecosystem. Services must be typed by hand; the macro for this is still open issue #231. Reflection, health checking and interceptor libraries are not documented.
- Production or security-sensitive systems. The README says wtx has had no security audit. In issue #452 (Nov 2025) the author calls it 'a fun project developed in my free-time that probably shouldn't be used in production' and advised a user to stay on tokio-tungstenite.
- Small CPU budgets or strict tail-latency targets. In grpc_bench's 2026-04-23 run (wtx 0.40, 1-4 server CPUs, 1000 clients), wtx trailed go_grpc (93,004 vs 117,082 req/s at 4 CPUs) and tonic, and its p90 stayed at about 42 ms. On HttpArena its p99 was 69.93 ms at 256 connections (average 6.55 ms), and it used 727 MiB of memory against grpc-go's 310.5 MiB.
- Teams that require stable Rust or a stable API. lib.rs enables nightly features, and crates.io lists 7 breaking minor releases (0.46 to 0.52) between 2026-05-16 and 2026-08-10.

## How it is fast

Http2ServerFramework::run_in_threads uses a runtime-per-thread, shared-nothing design. It starts one single-threaded tokio LocalRuntime per available thread. Each runtime binds its own listener (SO_REUSEPORT is on by default) and runs its connection and stream tasks locally, so the hot path has no work-stealing and no cross-thread handoff. The HTTP/2 framing, HPACK and Huffman code are written in-house, and the response is built in the same buffer as the request, so a reply no larger than the request needs no new allocation. The benchmark binary also used target-cpu=native, thin LTO, codegen-units=1, panic=abort and wtx's optimizations-std feature (memchr, simdutf8, socket2).

## Compared with alternatives

Pick wtx when the service is written in Rust and must keep standard gRPC-over-HTTP/2 clients: its measured gain over grpc-go (3.7-5.5x) is larger than that of Kitex (1.5-1.7x) or rpcx (2.3-2.6x), both Go, though each was measured on a different harness. grpcxx is the closest C++ analogue that also speaks gRPC; brpc is the more mature C++ multi-protocol choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | For the benchmarked gRPC server: tokio, quick-protobuf, hashbrown, foldhash, plus memchr, simdutf8 and socket2 through optimizations-std. pb-rs (or another generator) is needed at build time to generate message types. TLS or other crypto needs one backend feature: crypto-ring (ring), crypto-alr (aws-lc-rs), crypto-graviola or crypto-ruco (RustCrypto). |
| **Minimum toolchain** | Rust nightly only. lib.rs uses #![feature(random, return_type_notation)] even though crates.io lists rust-version 1.96. The repo pins nightly-2026-09-03, the crate uses edition 2024, and HttpArena built wtx 0.49 with nightly-2026-06-27. |
| **Platforms** | The core is no_std + alloc, and the README says it works on embedded devices with a heap allocator. Targets with 16-bit pointers are not supported. The multi-threaded server needs std; the executors are tokio, wtx's own std executor, and embassy-net. Benchmarks exist only for x86-64 Linux. |
| **Thread safety** | run_in_threads gives each thread its own single-threaded runtime and its own clone of the application data, and each stream gets another clone. Shared mutable state must therefore live behind Arc or atomics inside that data. Http2ServerFramework::run, on a multi-threaded runtime, requires Send + Sync bounds. For TLS, the docs leave coordination between the concurrent reader and writer to the user. |
| **Drop-in for the baseline** | partial: it follows the gRPC over HTTP/2 wire spec, so standard gRPC clients over h2c or TLS+ALPN should work, but it is a Rust library with a different, unary-only, hand-routed server API rather than a replacement for grpc-go code |

## Gotchas

- The response is built in the request buffer, and the handler's return type decides what happens to that buffer. ResFinalizer for () (and for &str, String and Vector) calls req.clear(). A handler that writes its reply into req.msg_data.body and returns () therefore sends an empty body with grpc-status 0. This bug invalidated wtx's own HttpArena entry until PR #1300; return StatusCode or VerbatimParams instead.
- If no crypto backend feature is selected, crypto calls panic or halt at runtime instead of failing the build. TLS and secure cookies need one of crypto-ring, crypto-alr, crypto-graviola or crypto-ruco.
- HTTP/2 has no HTTP/1.1 Upgrade path. Clients must use prior-knowledge h2c or ALPN over TLS. Stream prioritization and server push are not supported.
- The README warns that wtx assumes the summed length of any number of slices cannot overflow. On 32-bit targets, oversized input can overflow and cause unexpected behavior. The docs also flag PlaintextCtx (the TLS config used for plain h2c) as dangerous if misconfigured.

## Known shortcomings

- Rust. The wtx and grpc-go HttpArena runs were weeks apart, the author contributed the entry, and earlier wtx numbers were invalid (empty reply body, fixed in PR #1300). Several other entries (zix, cardigan, swerver) reach \~6.8-7.0M rps on the same board.
- Unary gRPC calls only, with hand-written service definitions (#231) and third-party message codegen. The author calls it a free-time project that probably shouldn't be used in production (#452); no security audit, including its own TLS 1.3. An independent grpc_bench run (discussion #559, 2026-04, Xeon Gold 6548N, wtx 0.40) had it behind go_grpc (93,004 vs 117,082 req/s at 4 CPUs) and tonic, while an earlier run (#547, Ryzen 5900X) had it ahead, so the result depends on environment. HttpArena p99 is 69.9 ms at 256 connections vs a 6.55 ms average, and grpc-go's p99 field repeats its average, so tail latency cannot be compared. Returning () or a string type from a handler silently sends an empty body with grpc-status 0 (behind the invalid HttpArena results fixed in PR #1300). Needs nightly Rust; 7 breaking releases in 3 months (benchmarked 0.49, current 0.52.1). Plain HTTP/2 is slower than hyper (4.08M vs 6.97M req/s). Missing crypto feature fails at runtime, not build time.

## Caveats and trade-offs

wtx's server process used \~64 logical CPUs (6379-6383% cpu) versus grpc-go's \~44 (4339-4478% cpu) during the run, so throughput-per-core is not directly comparable, only end-to-end rps on shared hardware. The two results were not measured in the same session: grpc-go's unary-grpc numbers have been unchanged since an HttpArena results update on 2026-04-12 (commit f326f067), while wtx's current numbers come from a re-run on 2026-08-24 (PR #1300), and the harness evolved in between. wtx's earlier published unary-grpc numbers (2026-07-30 to 2026-08-24) were invalid: its handler returned an empty reply body that h2load did not detect; body validation caught it, the entry was disabled (PR #1291), fixed and re-validated in PR #1300. The figures above are the post-fix validated numbers. The harness (HttpArena, github.com/MDA2AV/HttpArena, MIT-licensed) is a general full-stack web-framework benchmark, not an RPC-specific shootout. The wtx-grpc entry was contributed by wtx's own author (c410-f3r, PRs #812 and #1056), so it is not a fully arms-length third party, although the Dockerfiles, build commands and raw JSON results are public and runs are done centrally by the HttpArena maintainers. grpc-go is labeled 'tuned' but runs a default grpc.NewServer(). tonic (Rust's main gRPC framework) has a directory in the repo and was benchmarked in an April 2026 pre-round (378,723 rps at 256 connections, commit 2b36f907), but it is absent from the current results, so no current same-language comparison exists. wtx is not the fastest entry on the board: zix, cardigan and swerver post about 6.8-7.0M rps in the same test.

wtx is a multi-protocol crate (gRPC, HTTP/2, WebSocket, Postgres, TLS, etc.) rather than a dedicated RPC-only library; requires nightly Rust; small community and, per its own README, 'not widely used and has not undergone security audits'; used noticeably more memory (727MiB-1022MiB) than grpc-go (310-922MiB) in this test.

## Maintenance

Actively developed, almost entirely by one author (764 of about 790 non-bot commits; last commit 2026-09-08; 0.52.1 released 2026-08-14; about 70k crates.io downloads). The crate is MPL-2.0 and easy to depend on, but it is pre-1.0 with breaking releases every few weeks, nightly-only, unaudited, and its author does not recommend it for production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** http-arena.com/data.json results unary-grpc-256/1024 list wtx (3,990,708 / 3,620,970 rps) and grpc-go (720,798 / 969,718 rps) on the same board; benchmark code is public in MDA2AV/HttpArena (frameworks/wtx-grpc, frameworks/grpc-go, h2load harness), with toolchains and flags in the Dockerfiles/Cargo.toml and the CPU model (Threadripper PRO 3995WX) stated in the hardware docs and data.json.
- **Verifier notes:** Numbers, ratios (5.54x at 256 conns, 3.73x at 1024 conns), and all repository metadata (MPL-2.0, 401 stars, last commit 2026-09-08, not a fork, not archived) are confirmed. The corrections make the hardware description precise (the server gets 32 physical cores plus SMT, not 64 dedicated cores), add the exact toolchains and workload parameters, and add caveats about the different run dates and wtx's earlier invalid, since-fixed result. Tier A stays.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://www.http-arena.com/data.json>
  - <https://www.http-arena.com/>
  - <https://github.com/c410-f3r/wtx>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/wtx-grpc>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/Cargo.toml>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/meta.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/grpc-go>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/grpc-go/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/grpc-go/main.go>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/grpc-go/go.mod>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/grpc-go/meta.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/tonic-grpc>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/tonic-grpc/meta.json>
  - <https://github.com/MDA2AV/HttpArena/blob/main/site/data/results/grpc-go.json>
  - <https://github.com/MDA2AV/HttpArena/blob/main/site/content/docs/hardware/_index.md>
  - <https://github.com/MDA2AV/HttpArena/blob/main/site/content/docs/test-profiles/grpc/unary/_index.md>
  - <https://github.com/MDA2AV/HttpArena/blob/main/site/content/docs/test-profiles/grpc/unary/implementation.md>
  - <https://github.com/MDA2AV/HttpArena/commit/b33887a9>
  - <https://github.com/MDA2AV/HttpArena/commit/75baed4b>
- **Sources the enricher read:**
  - <https://github.com/c410-f3r/wtx>
  - <https://github.com/c410-f3r/wtx/blob/main/README.md>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx-docs/src/grpc/README.md>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx-docs/src/http2/README.md>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx-docs/src/http2-server-framework/README.md>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx-docs/src/executor/README.md>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx-docs/src/tls/README.md>
  - <https://github.com/c410-f3r/wtx/blob/main/rust-toolchain>
  - <https://github.com/c410-f3r/wtx/blob/main/SECURITY.md>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/Cargo.toml>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/lib.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/grpc.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/grpc/grpc_manager.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/http/http2_server_framework.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/http/http2_server_framework/res_finalizer.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/net/tcp_params.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/net/tokio.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx/src/executor/tokio_executor.rs>
  - <https://github.com/c410-f3r/wtx/blob/main/wtx-examples/examples/grpc-server.rs>
  - <https://github.com/c410-f3r/wtx/issues>
  - <https://github.com/c410-f3r/wtx/issues/452>
  - <https://github.com/c410-f3r/wtx/issues/234>
  - <https://github.com/c410-f3r/wtx/issues/231>
  - <https://github.com/c410-f3r/wtx/releases>
  - <https://github.com/c410-f3r/wtx/graphs/contributors>
  - <https://www.http-arena.com/data.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/wtx-grpc>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/Cargo.toml>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/meta.json>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/src/main.rs>
  - <https://github.com/MDA2AV/HttpArena/blob/main/frameworks/wtx-grpc/build.rs>
  - <https://github.com/MDA2AV/HttpArena/pull/1291>
  - <https://github.com/MDA2AV/HttpArena/pull/1300>
  - <https://github.com/LesnyRumcajs/grpc_bench>
  - <https://github.com/LesnyRumcajs/grpc_bench/blob/master/rust_wtx_bench/Cargo.toml>
  - <https://github.com/LesnyRumcajs/grpc_bench/pull/579>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/547>
  - <https://crates.io/api/v1/crates/wtx>
  - <https://crates.io/api/v1/crates/wtx/reverse_dependencies>
  - <https://hn.algolia.com/api/v1/search?query=wtx%20rust&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/c410-f3r/wtx`) · [data/wave5/enrich/raw/github_com_c410_f3r_wtx.json](../../../data/wave5/enrich/raw/github_com_c410_f3r_wtx.json) (enrichment confidence 0.78)

</details>
