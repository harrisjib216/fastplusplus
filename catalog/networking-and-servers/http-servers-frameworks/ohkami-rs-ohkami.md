# ohkami (nio backend)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust HTTP/1.1 web framework whose nio thread-per-core build out-served actix-web by \~11% on an empty-route benchmark.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | 181796.5 req/s (nio backend) vs actix-web 163414.7 req/s at concurrency 512 (\~11% faster; derived from page data); the same framework's tokio backend scored 168140.8 req/s (\~3% faster, within noise) |
| **Workload** | the-benchmarker/web-frameworks: GET / (empty body), zrk --closed closed loop over keep-alive connections, \~15s run, concurrency 512, server container pinned to \~4 cores (server_cpu_cores \~3.95, saturation \~0.99) with the load generator on disjoint cores; data.json revision of 2026-09-24 |
| **Metric** | throughput |
| **Hardware** | benchmark metadata reports 16 vCPUs, cpu_name 'M1 Eight-Core Processor', machine 'x86_64' (self-contradictory, see caveats) |
| **Adoption** | 332 stars |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/ohkami-rs/ohkami) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/master/data.json) |

## Verdict

In the-benchmarker/web-frameworks develop-branch data.json (2026-09-24; zrk --closed, GET / with an empty body, keep-alive, 15 s), the server container was pinned to \~4 cores (98.7-98.8% CPU saturation for both frameworks) on a host whose metadata reads both 'M1 Eight-Core Processor' and x86_64. There, ohkami 0.24 on nio did 181,797 req/s at c=512 vs actix-web 4.8 at 163,415 (+11%), with +2.7% at c=64 and +11.6% at c=256; both were built with Rust 1.98, fat LTO, codegen-units=1 and panic=abort. The ohkami tokio build was only +3%, and the older master-branch data.json (updated 2026-09-20, an earlier method revision) had ohkami-nio behind actix (74,657 vs 99,835 req/s at c=512; 84,831 vs 115,638 at c=64), so the nio lead depends on the load model.

## Use it when

- Linux HTTP/1.1 REST/JSON services with small requests over keep-alive connections, where you want more req/s per core than actix-web or hyper and can accept a pre-1.0 framework.
- Handlers that are short and similar in cost, so pinning each connection to one nio worker (no migration, no stealing) does not create hot threads.
- One handler/middleware codebase that must run on native servers, Cloudflare Workers (wasm32) and AWS Lambda, or where you want OpenAPI generated from handler types without macros.
- When you will benchmark rt_nio against rt_tokio on your own traffic. Switching is one Cargo feature plus the main attribute (#[nio::main] vs #[tokio::main]).

## Skip it when

- You need HTTP/2 or HTTP/3 (README: not supported; TLS is HTTP/1.1-only), chunked request bodies (issue #583, open), or HTTP/1.0 clients (the reader requires 'HTTP/1.1' and answers 505).
- CPU-heavy or uneven handlers on rt_nio. Pinned connections never move to another worker, so one slow handler stalls every connection on its worker. Tokio's work stealing is the safer default here.
- Tail latency matters more than peak req/s. At c=512 ohkami-nio had a lower median than actix (2.45 vs 3.13 ms) but a higher p99 (3.94 vs 3.22 ms) and about 6x the standard deviation (1.08 vs 0.18 ms).
- You need actix-web's maturity. Ohkami is 0.24.x with breaking renames queued (fang-&gt;middleware, claw-&gt;handler::component; issues #602/#603), has \~1.6k crates.io downloads in the last 90 days, and nio is a 0.1.x runtime (first stable release Jan 2026, \~7.7k downloads) with one listed author.
- Choosing rt_smol for speed. smol::spawn runs on smol's global executor, which is single-threaded unless SMOL_THREADS is set. In the benchmark the smol build reached 53,077 req/s on \~1.15 of 4 cores.

## How it is fast

With rt_nio, the accept loop hands each connection to nio::spawn_pinned, which puts it on the least-loaded worker. conn.connect() then registers the socket with that worker's own mio reactor, so the connection's reads, writes and keep-alive timer stay on one thread with no work stealing, atomics or cross-thread wakeups (this is the 'thread-per-core' design in nio's announcement post). Ohkami's HTTP/1.1 path is its own code, not hyper: each connection reuses one 2 KiB read buffer, the request line and headers are parsed in place with header values borrowed as slices of that buffer, standard headers go in a byte-indexed fixed array, and routing uses a compressed radix tree of leaked static nodes. The tokio build runs the same request path on tokio's work-stealing scheduler and measured only \~3% over actix, so most of the margin follows the runtime choice.

## Compared with alternatives

In the same 2026-09-24 run, ohkami-nio (181.8k req/s at c=512) trailed may_minihttp (194.4k) but beat the C/C++ siblings measured there: CWIST 151.3k, Agoo-C 149.2k, Drogon 131.6k. Pick ohkami over may_minihttp when you need its framework layer (typed extractors, fangs, TLS, WebSocket, OpenAPI, Workers/Lambda targets), and over the C/C++ entries when you want a Rust codebase.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ohkami_lib, ohkami_macros, byte_reader, serde, serde_json, http, base64, hmac, sha2, uuid, plus exactly one runtime crate chosen by feature (rt_nio pulls nio 0.1.3 with tokio-io traits; nio itself uses mio and crossbeam). Optional: rustls + anysc-rustls (tls), mews (ws), ohkami_openapi (openapi), tracing. |
| **Minimum toolchain** | Rust edition 2024. README MSRV is 'latest stable', and CI runs stable and nightly. The benchmark built with Rust 1.98. |
| **Platforms** | Native runtimes: CI runs only on ubuntu-latest for both ohkami and nio (mio-based); other OSes not documented. Also wasm32 via rt_worker (Cloudflare Workers) and AWS Lambda via rt_lambda. |
| **Thread safety** | On tokio, smol and lambda builds the compiler enforces Send + Sync + 'static on handlers and fangs. On rt_nio those bounds are dropped, but the router is shared across nio worker threads through an unsafe impl Send/Sync, so keeping handler and Context state thread-safe is up to you. |
| **Drop-in for the baseline** | no |

## Gotchas

- rt_nio soundness hole: SendSyncOnThreaded becomes a blanket impl when __rt_threaded__ is off, yet nio_rt.rs does 'unsafe impl Send/Sync for Router' and spawns sessions on several workers. Handler or Context state built on Rc, RefCell or Cell compiles and can race.
- The native reader does one read() per request into the fixed buffer (request_bufsize, default 2 KiB) and parses only what arrived. A request head larger than the buffer or split across reads fails with 431 (raise OHKAMI_REQUEST_BUFSIZE). It also requires exactly ': ' after each header name, and bytes of a pipelined second request in the same read are zeroed, not queued.
- Router construction leaks memory on purpose (Vec::leak for route nodes and allowed-method strings; issue #643, open). That is harmless for one long-lived server but accumulates if you rebuild Ohkami instances in-process (tests, hot reload).
- GET, HEAD and OPTIONS requests with a nonzero Content-Length are rejected with 400. Config::default() ignores the OHKAMI_\* environment overrides; use Config::new() if you want them.

## Known shortcomings

- The nio win holds on the suite's develop-branch run (2026-09-24: +2.7% to +11.6% over actix), but on the earlier master revision (2026-09-20) ohkami-nio trails actix badly (74,657 vs 99,835 req/s at c=512) while ohkami-tokio wins, so the result depends on the load model; the linked master data.json lacks the claimed numbers. nio is a thread-per-core async runtime on mio (0.1.x, one author), not a 'non-async runtime'. With rt_nio, handler Send/Sync bounds are dropped and the Router gets an unsafe impl Send/Sync while sessions run on several threads, so Rc/RefCell state compiles and can race. HTTP/1.1 reader does one read into a 2 KiB buffer (larger or split heads get 431), requires exactly ': ', rejects HTTP/1.0, discards pipelined requests; no chunked request bodies (#583), HTTP/2 or HTTP/3. At c=512 its p99 is higher than actix (3.94 vs 3.22 ms) with \~6x the stdev. Pre-1.0 (0.24.9) with breaking renames queued; router construction leaks memory on purpose (#643); Ubuntu-only CI. Benchmark builds: Rust 1.98, fat LTO, codegen-units 1, panic=abort.

## Caveats and trade-offs

Only the nio variant clears a meaningful margin (\~11%); the more commonly deployed tokio variant is only \~3% ahead, which the suite's README says to treat as noise until repeated (it states no numeric noise threshold); the smol variant is far slower (53076.6 req/s); single synthetic route; the suite changed load generator and model in 2026 and says results from different revisions are not comparable; hardware metadata inconsistent ('M1 Eight-Core Processor' on x86_64)

The `nio` (non-async-runtime) backend trades the mature tokio ecosystem for speed; the framework overall is younger and less battle-tested in production than actix-web

## Maintenance

Actively maintained (last commit 2026-08-25; latest crates.io release 0.24.9 on 2026-04-12, 78 versions since 2022) and MIT-licensed as an ordinary crate, but still pre-1.0 with open breaking-change issues. The nio runtime behind the headline number is Apache-2.0 and 0.1.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (the-benchmarker/web-frameworks data.json, updated 2026-09-24) shows ohkami-nio (id 3169) at 181796.54 req/s and ohkami-tokio (id 3187) at 168140.83 req/s vs actix (id 3052) at 163414.69 req/s at c=512. The code is public, but there are no compiler flags and the CPU model metadata is contradictory, so it is not A.
- **Verifier notes:** All three ohkami figures and the actix figure match data.json exactly, and the derived ratios are correct. The workload was corrected from 'oha, keep-alive disabled' to the current zrk keep-alive method. The caveat's 'noise threshold' wording was softened because the README gives only qualitative guidance. Metadata checked: MIT, 332 stars, last commit 2026-08-25, not a fork.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/README.md>
  - <https://github.com/ohkami-rs/ohkami>
- **Sources the enricher read:**
  - <https://github.com/ohkami-rs/ohkami>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/README.md>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/Cargo.toml>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/Cargo.toml>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/lib.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/config.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/session/mod.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/ohkami/mod.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/ohkami/specialize/nio_rt.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/request/mod.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/request/headers.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/router/final.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/fang/mod.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/fang/bound.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/ohkami/src/fang/handler/mod.rs>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/benches_rt/Cargo.toml>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/benches_rt/nio/Cargo.toml>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/benches_rt/vs_actix-web/Cargo.toml>
  - <https://raw.githubusercontent.com/ohkami-rs/ohkami/main/.github/workflows/CI.yml>
  - <https://github.com/ohkami-rs/ohkami/issues>
  - <https://github.com/ohkami-rs/ohkami/issues/643>
  - <https://github.com/ohkami-rs/ohkami/issues/594>
  - <https://github.com/ohkami-rs/ohkami/issues/583>
  - <https://github.com/ohkami-rs/ohkami/issues/286>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/rust/ohkami-nio>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/rust/ohkami-tokio>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/rust/actix>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/rust/config.yaml>
  - <https://github.com/nurmohammed840/nio>
  - <https://raw.githubusercontent.com/nurmohammed840/nio/main/libs/nio-rt/Cargo.toml>
  - <https://raw.githubusercontent.com/nurmohammed840/nio/main/.github/workflows/ci.yml>
  - <https://nurmohammed840.github.io/posts/embracing-thread-per-core-architecture/>
  - <https://raw.githubusercontent.com/smol-rs/smol/master/src/spawn.rs>
  - <https://crates.io/api/v1/crates/ohkami>
  - <https://crates.io/api/v1/crates/nio>
  - <https://hn.algolia.com/api/v1/search?query=ohkami&tags=story>
  - <https://rustsec.org/packages/ohkami.html>
  - <https://rustsec.org/packages/nio.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ohkami-rs/ohkami`) · [data/wave5/enrich/raw/github_com_ohkami_rs_ohkami.json](../../../data/wave5/enrich/raw/github_com_ohkami_rs_ohkami.json) (enrichment confidence 0.4)

</details>
