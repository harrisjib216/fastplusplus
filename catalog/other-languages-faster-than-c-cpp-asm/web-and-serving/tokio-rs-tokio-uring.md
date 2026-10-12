# tokio-uring (HttpArena minimal HTTP/1.1 server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟡 stale

> io_uring-backed Rust runtime; a hand-rolled HTTP/1.1 server on it edges nginx 1.09x in HttpArena but loses to plain epoll tokio.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native) in the HttpArena suite; h2o, mongoose, libreactorng, libioma (C) and Drogon, Cutelyst, hical, agensio, userver (C++) rows alongside |
| **Claimed result** | baseline-4096: 3,565,878 req/s vs nginx 3,284,513 (1.09x, derived from page data), Drogon 2,022,710 (1.76x), hical 3,228,043 (1.10x), agensio 3,558,559 (1.00x); level with or behind h2o 3,641,609 (0.98x), mongoose 3,707,598 (0.96x). pipelined-4096: 48,876,057 vs nginx 4,037,345 (12.1x), Drogon 7,801,404 (6.27x) and libreactorng (C, io_uring) 43,424,448 (1.13x). limited-conn-4096: 2,636,459 vs nginx 2,626,297 (1.00x, a tie). |
| **Workload** | HttpArena H/1.1 profiles (baseline with 4096 connections, pipelined, limited-conn) on one 64-core machine; the entry is a hand-written HTTP/1.1 parser on tokio-uring (io_uring completion API, owned buffers), one runtime per core with SO_REUSEPORT, no HTTP framework. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (HttpArena site/data/current.json and site/content/docs/hardware/_index.md). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) and the load generator (gcannon for H/1.1, h2load for HTTP/2) to 32-63,96-127 over loopback; 5 s runs, best of 3 (scripts/lib/common.sh, scripts/lib/profiles.sh, scripts/benchmark.sh). |
| **Compiler and flags** | tokio-uring entry: rust:1.95 image, RUSTFLAGS='-C target-cpu=native' cargo build --release with opt-level 3, codegen-units 1, thin LTO, panic=abort, tokio-uring 0.5 (frameworks/tokio-uring/Dockerfile and Cargo.toml). C/C++ rows: nginx 1.31.4 with a custom handler module, Debian trixie toolchain, --with-cc-opt='-O3 -march=native -DNDEBUG'; h2o clang CMake Release -march=native -mtune=native (no LTO); mongoose gcc-14 -O3 -march=native -flto; Drogon CMake Release in the unpinned drogonframework/drogon:latest image with jemalloc preloaded; hical gcc-14 CMake Release -march=native -mtune=native; libreactorng -O3 -march=native (HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | io_uring completion-based I/O with owned buffers and one runtime per core sharding accepts through SO_REUSEPORT, against nginx on epoll (HttpArena entry description; the repo gives no claim). |
| **Adoption** | 1.5k stars (tokio-uring); the server itself is an HttpArena entry |
| **Last commit** | 2025-07-07 |
| **Links** | [repository](https://github.com/tokio-rs/tokio-uring) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio-uring.json) |

## Verdict

In HttpArena on a Threadripper PRO 3995WX (server pinned to 32 cores / 64 threads, gcannon load over loopback, 5 s runs, best of 3), the hand-rolled tokio-uring HTTP/1.1 server (rust 1.95, target-cpu=native, opt-level 3, thin LTO) served 3,565,878 req/s at baseline-4096 vs nginx 1.31.4 (custom handler module, -O3 -march=native) 3,284,513 (1.09x), 48,876,057 vs 4,037,345 pipelined at depth 16 (12.1x), and tied nginx at limited-conn-4096 (2,636,459 vs 2,626,297); h2o, mongoose, libioma, libreactorng and the plain epoll tokio entry are faster at baseline.

## Use it when

- Linux-only services (kernel 5.10+ per lib.rs, 5.11+ per README) where you control the kernel and container security profile and want a thread-per-core, shared-nothing design.
- Workloads that mix network and file I/O and benefit from submitting file reads/writes asynchronously through the same ring (tokio::fs uses a blocking thread pool instead).
- Experiments or research on completion-based I/O in Rust where a fork or vendored copy is acceptable.
- Heavily pipelined HTTP/1.1 microbenchmarks, where batching responses per read gives 48.9M req/s against nginx's 4.0M in HttpArena (though plain tokio does 54.8M with the same design).

## Skip it when

- If you only want faster networking than nginx: HttpArena's plain tokio (epoll) entry with the same hand-rolled parser and flags beats tokio-uring on every shared profile (baseline-4096 4,187,085 vs 3,565,878 req/s) and uses less CPU per request at a fixed 1M req/s (18.7 vs 25.3 us).
- Connection-churn workloads: in limited-conn-4096 (10 requests per connection, 1.32M reconnects) its p99 is 20.50 ms against 2.36 ms for tokio and 7.65 ms for nginx.
- Default Docker or Kubernetes containers: Docker's default seccomp profile (defaultAction SCMP_ACT_ERRNO, no io_uring_\* syscalls allowed) makes io_uring_setup fail; HttpArena runs the server with --security-opt seccomp=unconfined and --ulimit memlock=-1:-1.
- Production code that needs a maintained dependency: last release 0.5.0 on 2024-05-27, last commit 2025-07-07, 57 open issues and 41 open PRs, a maintainer called it a 'bus factor problem' (issue #281) and issue #336 'Is tokio-uring safe for production?' has no maintainer reply.
- Code that needs Tokio's multi-thread work-stealing scheduler or Send futures: tasks are spawned with spawn_local on a current_thread runtime and resource types are mostly !Sync (multi_thread support is open issue #258).

## How it is fast

The server starts one tokio_uring::start runtime per available CPU, each with its own SO_REUSEPORT listener, so accepts are sharded by the kernel and no task crosses threads. Each connection parses every complete request in its buffer and writes all responses in one write_all, which is what makes the pipelined profile (depth 16) 12x nginx. Responses are a minimal 63 bytes (no Date or Server header) against about 135 for nginx. The io_uring use is the basic one: one-shot accept/read/write submissions with a 16 KiB owned Vec per read and the default 256-entry ring; the crate's registered-buffer calls (read_fixed/write_fixed) are not used, and provided-buffer rings (issue #112), multishot recv and SQPOLL are not involved.

## Compared with alternatives

Pick the Rust raw tokio HttpArena entry over this one for HTTP serving: same parser, same flags, faster on every profile and cheaper per request; pick tokio-uring only when you specifically need io_uring file I/O in the same thread-per-core runtime. Among io_uring servers in the suite, ioxide (MDA2AV, 4,111,381 req/s), vanilla-io_uring (4,307,987) and libreactorng (4,377,377) all post higher baseline-4096 numbers.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio 1.x (net, rt, sync), io-uring 0.6, slab, libc, socket2 0.4, futures-util; optional bytes |
| **Minimum toolchain** | Rust edition 2018, no MSRV declared (issue #239 open); HttpArena builds with rust:1.95. Linux kernel 5.10+ (lib.rs docs) or 5.11+ (README says 5.4 does not work). |
| **Platforms** | Linux only (io_uring); x86-64 and aarch64 wherever the kernel supports io_uring. Containers need a seccomp profile that allows io_uring_setup/enter/register. |
| **Thread safety** | Single-threaded per runtime: tokio_uring::start runs a current_thread runtime with a LocalSet, tasks use spawn_local, most resource types are !Sync; scale by starting one runtime per thread. |
| **Drop-in for the baseline** | partial — not a replacement for nginx at all (you write the server yourself); against tokio::net it is a different API (buffers passed by ownership, explicit close()), though Tokio-based libraries still run inside its runtime. |

## Gotchas

- TcpListener::accept is not cancellation safe (open bug #129): dropping a partly polled accept future, e.g. losing a select! race or a timeout, leaks the accepted fd until the process exits; dropping other ops also cannot recover the buffer until the kernel completes it.
- Resources closed only on drop are closed in the background at an unspecified time (lib.rs 'Closing resources'); call close().await explicitly for deterministic fd release.
- Harness note: the measured server sends no Date or Server header (63 bytes per response vs about 135 for nginx, derived from bandwidth/req/s), routes only /pipeline and treats every other path as the a+b endpoint, so per-request work is lighter than nginx's; the io_uring path itself is not the reason for any lead, since the identical epoll tokio server is 1.17x faster at baseline-4096.
- CHANGELOG.md stops at 0.4.0 (2022-11-05); 0.5.0 changes are undocumented there.

## Known shortcomings

- HttpArena: the suite's plain epoll tokio entry beats it (4,187,085 vs 3,565,878 at baseline-4096), so io_uring is not the reason for the win; the hand-rolled server sends about 63 vs nginx's about 135 bytes per response (unequal work); behind libreactorng, libioma, mongoose and h2o. Last commit 2025-07-07.
- No correctness bug behind the numbers, but io_uring is not the reason for the lead: the same-design epoll tokio entry is faster on every profile and cheaper per request at a fixed 1M req/s (18.7 vs 25.3 us CPU per request on latency-1m-1024); limited-conn-4096 p99 is 20.50 ms against tokio's 2.36 ms and nginx's 7.65 ms. The entry uses only one-shot operations (no read_fixed, no buffer rings), sends no Date or Server header (63 vs about 135 bytes for nginx), and runs with seccomp=unconfined because Docker's default seccomp profile blocks io_uring_\* (EPERM). Open bug #129: accept leaks an fd on cancel; the crate is stale (0.5.0, 2024-05-27; maintenance issues #281 and #336 unanswered).

## Caveats and trade-offs

Not an io_uring win: the suite's plain tokio entry (epoll, same hand-rolled parser design, same Rust flags) is faster than tokio-uring on every shared profile (baseline-4096 4,187,085 vs 3,565,878; limited-conn-4096 2,721,455 vs 2,636,459; pipelined-4096 54,755,795 vs 48,876,057). The entry is a minimal hand-rolled server written for HttpArena (no maintainer listed, not the tokio-uring project's own code): it routes only /pipeline and answers every other path with the a+b sum, and sends about 63 bytes per response against about 135 for nginx (Date and Server headers; derived from page data, bandwidth over req/s), so the per-request work is not the same. At baseline-4096 it is behind libreactorng (4,377,377), libioma (4,255,834), mongoose (3,707,598) and h2o (3,641,609) and level with agensio; at limited-conn-4096 it ties nginx (1.00x) and is behind libioma, mongoose, libreactorng and h2o. The large pipelined ratio is on a reference-only profile (pipeline depth 16) and mostly reflects nginx's pipelining cost. 5 s runs, best of 3, server limited to 32 of 64 cores; results files are undated. The tokio-uring README states no benchmark numbers and calls the project 'still very young'; last commit 2025-07-07. [retier] The same-design epoll tokio entry is faster on every profile and cheaper per request at a fixed 1M req/s (18.7 vs 25.3 us CPU per request); limited-conn-4096 p99 is 20.50 ms against tokio's 2.36 ms and nginx's 7.65 ms. The entry uses only one-shot operations (no read_fixed, no buffer rings), sends no Date or Server header (63 vs about 135 bytes for nginx), and runs with seccomp=unconfined. Open bug #129: accept leaks an fd on cancel; crate stale (0.5.0, 2024-05-27).

tokio-uring needs Linux with io_uring and is still described by its README as very young (filesystem and network operations); the HttpArena server is a minimal hand-rolled parser, not a framework; the repo's last commit is from July 2025.

## Maintenance

Stale but MIT-licensed: last release 0.5.0 (2024-05-27), last commit a clippy/rustfmt fix on 2025-07-07, open questions about maintenance (#281, #336) unanswered by maintainers, so treat it as usable for experiments and vendorable, not as a maintained production dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A on the HttpArena precedent: every quoted number matches site/data/results/tokio-uring.json and the sibling nginx/drogon/hical/agensio/h2o/mongoose/libreactorng JSON files; the code is public (frameworks/tokio-uring/{Dockerfile,Cargo.toml,src/main.rs}, frameworks/nginx/{Dockerfile,nginx.conf}, scripts/benchmark.sh, scripts/lib/profiles.sh), Rust and nginx flags are in the Dockerfiles and Cargo.toml, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json.
- **Verifier notes:** All quoted numbers verified; tier raised to A on the HttpArena precedent. Shortcomings to record: the record's why_faster (io_uring) is contradicted by the suite's own epoll tokio entry, which beats tokio-uring 1.17x at baseline-4096; minimal hand-rolled handler sending about half nginx's response bytes (same_algorithm false); behind four C servers at baseline and limited-conn; pipelined is reference-only. Metadata confirmed: MIT, 1.5k stars, last commit 2025-07-07 (stale), not a fork, not archived.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-43 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio-uring.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/frameworks.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/tokio-uring.json>
  - <https://github.com/tokio-rs/tokio-uring>
  - <https://github.com/tokio-rs/tokio-uring/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio-uring/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio-uring.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/framework.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/README.md>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/src/runtime/mod.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/src/net/tcp/stream.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/src/net/tcp/listener.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-uring/HEAD/src/buf/mod.rs>
  - <https://github.com/tokio-rs/tokio-uring>
  - <https://github.com/tokio-rs/tokio-uring/commits>
  - <https://github.com/tokio-rs/tokio-uring/issues?q=is%3Aissue+is%3Aopen+sort%3Acomments-desc>
  - <https://github.com/tokio-rs/tokio-uring/issues/281>
  - <https://github.com/tokio-rs/tokio-uring/issues/336>
  - <https://github.com/tokio-rs/tokio-uring/issues/129>
  - <https://crates.io/api/v1/crates/tokio-uring>
  - <https://raw.githubusercontent.com/moby/profiles/HEAD/seccomp/default.json>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/tokio-rs/tokio-uring`) · [data/wave14/enrich/raw/github_com_tokio_rs_tokio_uring.json](../../../data/wave14/enrich/raw/github_com_tokio_rs_tokio_uring.json) (enrichment confidence 0.75)

</details>
