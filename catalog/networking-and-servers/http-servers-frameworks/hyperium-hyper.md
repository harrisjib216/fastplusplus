# hyper

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust's low-level HTTP/1 and HTTP/2 library under axum and warp; raw hyper roughly ties actix-web on minimal GET /.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop commit f673364): hyper 1.5 173,608 / 168,763 / 166,617 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 0.97x / 1.00x / 1.02x (derived from page data). The earlier snapshots (older harness method) show a clearer lead: commit 0fccb1d (2026-09-20, on master) 133,784 / 113,798 / 110,895 vs 115,638 / 102,329 / 99,835 = 1.16x / 1.11x / 1.11x; commit 8ae370a (2026-09-18) 136,278 / 113,266 / 110,589 vs 117,177 / 100,171 / 98,722 = 1.16x / 1.13x / 1.12x (derived from page data) |
| **Workload** | the-benchmarker/web-frameworks run of 2026-09-24 (data.json updated_at 2026-09-24 06:59 UTC, develop commit f673364): GET / (empty body) on the suite's minimal per-framework app, load from `zrk --plain --closed` (a closed loop over keep-alive connections, not wrk) after a 5 s warmup at c=50, 15 s runs at concurrency 64/256/512, server container on \~4 cores (server_cpu_cores \~3.95, saturation \~0.99) with the load generator on separate cores; values are averages of the stored samples |
| **Metric** | throughput |
| **Hardware** | Single host per data.json: 16 CPUs, 7,733,008 kB RAM, Linux 7.2.6-200.fc44.x86_64 (x86_64); the cpu_name 'M1 Eight-Core Processor' is a string hard-coded in .tasks/db.rake, not a measured CPU model; server container used \~3.95 cores; run dated 2026-09-24 |
| **Compiler and flags** | Rust 1.98 (rust:1.98-slim image), `cargo build --release` with opt-level=3, lto=true, codegen-units=1, panic=abort (rust/hyper/Cargo.toml, rust/Dockerfile); hyper 1.5 + hyper-util 0.1 on a multi-thread tokio runtime. Baseline actix-web 4.8 uses the same toolchain and release profile |
| **Adoption** | 16.3k stars; underlies axum, warp, and much of the Rust HTTP ecosystem |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/hyperium/hyper) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

the-benchmarker/web-frameworks run of 2026-09-24 (commit f673364): GET / with an empty body, zrk closed loop over keep-alive connections, 15 s at c=64/256/512, server pinned to about 4 cores of a 16-CPU x86-64 Linux host (real CPU model not stated), both apps built with Rust 1.98, LTO, codegen-units=1, panic=abort. Raw hyper with a hand-written match router did 173.6k / 168.8k / 166.6k req/s vs actix-web's 179.2k / 168.3k / 163.4k (0.97x / 1.00x / 1.02x); the earlier 1.11-1.16x lead comes from snapshots taken before the harness was changed to a sized, pinned closed-loop generator, which the suite says are not comparable, and each level is one stored sample, so run-to-run variance is unknown.

## Use it when

- Building your own framework, reverse proxy, gateway or RPC layer on tokio where you need direct control of connections, upgrades and HTTP/2 rather than a router.
- Small fixed-route services (health checks, sidecars, metrics or webhook endpoints) where a hand-written match router is enough and you want to skip framework overhead: raw hyper served 17-19% more req/s than axum 0.8 at every concurrency in the 2026-09-24 run.
- You need both an HTTP client and server on the same stack (reqwest, axum and warp all sit on hyper), or HTTP/2 alongside HTTP/1.
- You want throughput on par with actix-web while staying in the tokio/tower ecosystem.

## Skip it when

- You expect a throughput win over actix-web: under the suite's current method (sized generator, server at \~99% CPU) the result is 0.97x / 1.00x / 1.02x at c=64 / 256 / 512, which the suite itself says to treat as noise until repeated.
- Tail latency under saturation matters: with equal medians, hyper's p99 was 2.55 ms vs actix-web's 1.58 ms at c=256 and 6.03 ms vs 3.22 ms at c=512 (8.45 vs 4.56 ms at c=512 in the 2026-09-20 snapshot too). actix-web runs one sequential worker per physical CPU; the hyper app uses tokio's multi-thread runtime.
- You want routing, extractors, middleware, TLS and graceful shutdown out of the box; with raw hyper you assemble them from hyper-util, tower or your own code, and the hyper guide calls hyper-util less stable than hyper.
- Very many mostly idle HTTP/1 connections on tight memory: each connection allocates an 8 KiB read buffer, and open issue #4060 reports header Bytes keeping large IO buffers alive in an h2-to-h1 proxy.

## How it is fast

Requests are parsed by httparse, a zero-copy push parser with SSE4.2, AVX2 and NEON backends plus a SWAR fallback; hyper keeps up to 100 header slots in a stack SmallVec, records header positions as indices, then freezes the read buffer into refcounted Bytes so the URI, header names and values share one allocation. The read buffer starts at 8 KiB and adapts (doubles when a read fills it, shrinks only after two consecutive short reads); the Date header is cached per thread and reformatted at most once per second; writes are either flattened into one buffer or queued for writev, and the opt-in pipeline_flush aggregates flushes across pipelined requests. In the benchmark most of the gap to frameworks is simply missing framework layers: in the same run axum 0.8, which is built on hyper, did 141,410 req/s at c=512 against raw hyper's 166,617.

## Compared with alternatives

Pick hyper over may_minihttp or ohkami's nio backend when you need a mature, widely deployed HTTP/1 + HTTP/2 client/server on tokio with tower/axum compatibility; if raw GET throughput on a Rust stack is the goal, those siblings did better in the same run (194,372 and 181,797 req/s at c=512 vs hyper's 166,617), and may_minihttp also had a p99 of 2.71 ms vs 6.03 ms.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bytes, http, http-body, tokio (sync); with http1/server features also httparse, httpdate, itoa, atomic-waker, futures-core, smallvec, pin-project-lite; h2 for HTTP/2. In practice a server also needs hyper-util (TokioIo, auto HTTP/1+2, graceful shutdown), http-body-util and a tokio runtime. |
| **Minimum toolchain** | Rust 1.63 MSRV (edition 2021), policy is to support compilers at least 6 months old; the benchmark used Rust 1.98 |
| **Platforms** | any target std and tokio support; runtime-agnostic through hyper::rt Read/Write/Executor/Timer traits; httparse has x86-64 SSE4.2/AVX2 and aarch64 NEON paths with a SWAR fallback |
| **Thread safety** | Each connection is a future you spawn (one task per connection in the benchmark app); on tokio's multi-thread runtime the service future and body must be Send. Futures are documented as cancel safe: dropping an HTTP/1 request future closes that TCP connection, while HTTP/2 sends RST_STREAM for that stream only. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 30 s default header_read_timeout does nothing unless you set a Timer with Builder::timer; without hyper's unstable tracing feature there is not even a warning. The benchmark app sets no timer, so copying it leaves clients that send headers slowly with no time limit.
- The benchmark app enables pipeline_flush(true), which hyper documents as 'Experimental, may have bugs' (default false); it also forces the flatten write strategy.
- The suite's 'hyper 1.5' and 'actix 4.8' labels are Cargo version floors: only \*.rs and Cargo.toml are copied into the image (no Cargo.lock), so each build resolves the newest compatible release (hyper 1.11.1 since 2026-08-28).
- HTTP/2 goes through the h2 crate: advisory GHSA-q83h-524g-xf6h (2026-08-17, h2 &lt; 0.4.16) allowed unbounded queues of empty DATA frames when request or response bodies are not drained. Upgrade h2 and drain bodies.

## Known shortcomings

- The margin over actix flips between runs: 0.97x/1.00x/1.02x on 2026-09-24 but 1.11-1.16x in the two earlier runs. The suite's hyper app is raw hyper with a hand-written router, not a framework.
- The earlier 1.11-1.16x lead came from snapshots predating the suite's harness fix (67d90d2, 2026-09-15, 'Restore closed-loop zrk, size the generator'); the suite says revisions aren't comparable, and data.json stores one sample per level. p99 is worse than actix (2.55 vs 1.58 ms at c=256; 6.03 vs 3.22 ms at c=512). Version labels are floors (no Cargo.lock), so 'hyper 1.5' resolves to the newest compatible release. Raw hyper vs a full framework is apples-to-oranges: axum on hyper does 141,410 vs raw hyper's 166,617 req/s at c=512; may_minihttp and ohkami-nio beat hyper in the same run. The benchmark app enables experimental pipeline_flush(true) and sets no Timer, so the default header_read_timeout does nothing. h2 &lt; 0.4.16 is affected by GHSA-q83h-524g-xf6h (unbounded empty DATA frames).

## Caveats and trade-offs

In the cited run the margin is within noise (0.97x at c=64, 1.00x at c=256, 1.02x at c=512); under the older harness method (2026-09-18 and 2026-09-20 snapshots) hyper led actix by 11-16% at every level. The suite's hyper app is raw hyper with a hand-written match router and pipeline_flush(true), not a framework, and sends smaller responses (\~75 vs \~88 bytes per response received), so it is a lower-level library than actix-web. Single-route synthetic GET / benchmark; the CPU name is a hard-coded label.

hyper is a low-level HTTP library, not a full framework like actix-web, so the raw-hyper shootout entry has less framework overhead by construction (apples-to-oranges)

## Maintenance

Actively maintained (v1.11.1 released 2026-08-28, commits up to 2026-09-26, about 950M crates.io downloads), MIT-licensed with a stable 1.x API, but the server plumbing you need beyond a raw connection lives in the faster-moving hyper-util.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs hyper and actix in one run with public code and stated build flags (rust/hyper/src/main.rs, rust/hyper/Cargo.toml, rust/actix, rust/Dockerfile, .tasks/config.rake). Not A: the cpu_name is hard-coded in .tasks/db.rake, so no real CPU model is stated.
- **Verifier notes:** Numbers match data.json exactly (row id 3097 'hyper' 1.5; actix id 3052). Build flags are now confirmed, but the tier stays B because there is no real CPU model. benchmark_url is pinned to develop commit f673364, and the load tool is corrected from wrk to zrk --closed. Metadata verified via GraphQL: MIT, 16,333 stars, last commit 2026-09-26, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8ae370ae89075281c056a138e57de25682d36e02/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/config.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/hyper/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/hyper/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/hyper/src/main.rs>
  - <https://web-frameworks-benchmark.netlify.app/result?l=rust>
  - <https://github.com/hyperium/hyper>
- **Sources the enricher read:**
  - <https://github.com/hyperium/hyper>
  - <https://github.com/hyperium/hyper/blob/master/README.md>
  - <https://github.com/hyperium/hyper/blob/master/Cargo.toml>
  - <https://github.com/hyperium/hyper/blob/master/docs/MSRV.md>
  - <https://github.com/hyperium/hyper/blob/master/src/lib.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/rt/mod.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/proto/h1/io.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/proto/h1/role.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/common/date.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/common/time.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/trace.rs>
  - <https://github.com/hyperium/hyper/blob/master/src/server/conn/http1.rs>
  - <https://github.com/hyperium/hyper/security/advisories/GHSA-q83h-524g-xf6h>
  - <https://github.com/advisories?query=ecosystem%3Arust+hyper>
  - <https://github.com/hyperium/hyper/issues?q=label%3AC-performance>
  - <https://github.com/hyperium/hyper/issues/4060>
  - <https://github.com/hyperium/hyper/issues/4057>
  - <https://github.com/hyperium/hyper/issues/3258>
  - <https://github.com/hyperium/hyper/releases>
  - <https://crates.io/api/v1/crates/hyper>
  - <https://github.com/seanmonstar/httparse>
  - <https://github.com/seanmonstar/httparse/tree/master/src/simd>
  - <https://github.com/hyperium/hyperium.github.io/blob/master/_stable/server/graceful-shutdown.md>
  - <https://github.com/actix/actix-website/blob/main/docs/server.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/compare/0fccb1d5a502432d76dc1364ab6babf709ef1380...f673364fb30748e5bb8e57319ec2772bc872f78a>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/hyper/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/hyper/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/hyper/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/config.yaml>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/hyperium/hyper`) · [data/wave5/enrich/raw/github_com_hyperium_hyper.json](../../../data/wave5/enrich/raw/github_com_hyperium_hyper.json) (enrichment confidence 0.45)

</details>
