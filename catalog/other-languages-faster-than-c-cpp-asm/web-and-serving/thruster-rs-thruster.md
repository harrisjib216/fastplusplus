# Thruster (Rust, thruster-grpc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Koa-style Rust web framework whose experimental thruster-grpc server, on hyper/h2, out-served gRPC C++ in grpc_bench unary echo.

| | |
|---|---|
| **Beats** | gRPC C++ (grpc/grpc) servers cpp_grpc_st, cpp_grpc_mt and cpp_asio_grpc in the grpc_bench suite |
| **Claimed result** | grpc_bench complex_proto unary, ratios derived from page data. Latest run (discussion 559, 2026-04-23, commit c4c93b3): 1 server CPU rust_thruster_st 98,464 req/s and rust_thruster_mt 88,443 vs cpp_grpc_st 57,140, cpp_grpc_mt 57,403, cpp_asio_grpc 56,669 (st vs st 1.72x, mt vs mt 1.54x); 2 CPUs rust_thruster_mt 134,859 vs cpp_grpc_mt 74,574 (1.81x) and cpp_asio_grpc 74,869; 3 CPUs 138,576 vs 81,581 (1.70x); 4 CPUs 135,989 vs 85,485 (1.59x). Older run (wiki 2022-04-23, commit 14a8435): 1 CPU rust_thruster_st 41,334 (23.88 ms avg) vs cpp_grpc_st 26,700, cpp_grpc_mt 26,376, cpp_asio_grpc 24,926 (1.55x, 1.57x, 1.66x), rust_thruster_mt 36,793 (1.39x vs cpp_grpc_mt); at 2 CPUs rust_thruster_mt 56,740 vs cpp_grpc_mt 69,882 (0.81x) and at 3 CPUs 65,903 vs 71,806 (0.92x). |
| **Workload** | grpc_bench complex_proto unary SayHello echo: 50 client connections, 1000 concurrent requests, unlimited QPS, 120 s with 30 s warmup; server capped by docker --cpus at 1-4 CPUs (2026 run, 4096m RAM) or 1-3 CPUs (2022 run, 512m RAM). |
| **Metric** | throughput |
| **Hardware** | 2026-04-23 run (discussion 559): Intel Xeon Gold 6548N @ 2.80 GHz (16 cores shown), 64 GB RAM; server limited to 1-4 CPUs and 4096m RAM, ghz client on 11 CPUs, 120 s with 30 s warmup, 50 connections, 1000 concurrency. 2022-04-23 run (wiki): Intel Xeon E5-1650 v3 @ 3.50 GHz, 32 GB RAM; server limited to 1, 2 or 3 CPUs and 512m RAM, client 9 CPUs. |
| **Compiler and flags** | 2026-04 run at c4c93b3: rust_thruster_st/mt on the rust:1.94 image, cargo build --release --locked with opt-level 3, codegen-units 1, lto true, jemallocator; thruster 1.3.10 (hyper_server feature) plus thruster-grpc 0.2.3 on hyper 0.14 and prost 0.11; st runs tokio current_thread, mt a multi-thread runtime with GRPC_SERVER_CPUS workers. cpp_grpc_st/mt on the gcc:15.2.0 image: g++ -O3 -flto (mt adds --std=c++20) on main.cpp and the generated stubs, linked against Debian's prebuilt libgrpc++-dev and jemalloc (apt-get, unpinned; Debian's grpc package is 1.51.1, search snippet only), so the -O3 -flto flags never reach the gRPC core. 2022 run at 14a8435: rust:1.59 with thruster 1.2.2, thruster-grpc from git and hyper 0.13, same release profile; C++ on gcc:11 with the then-current Debian libgrpc++-dev (version not checked). HEAD has since moved the C++ images to gcc:16.1.0. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Single-threaded tokio current_thread runtime on hyper with jemalloc at a 1-CPU limit (inference from the benchmark setup; no source claim). |
| **Adoption** | 1.1k stars |
| **Last commit** | 2024-10-16 |
| **Links** | [repository](https://github.com/thruster-rs/Thruster) · [benchmark](https://github.com/LesnyRumcajs/grpc_bench/discussions/559) |

## Verdict

In LesnyRumcajs/grpc_bench (complex_proto unary echo, ghz with 50 connections, 1000 concurrency, 120 s after a 30 s warmup), the 2026-04 maintainer run on a Xeon Gold 6548N gave rust_thruster_st 98,464 req/s against cpp_grpc_st 57,140 at 1 server CPU (1.72x), and rust_thruster_mt 134,859-138,576 against cpp_grpc_mt 74,574-85,485 at 2-4 CPUs (1.59-1.81x). The C++ servers link Debian's prebuilt libgrpc++ under gcc 15.2 and the Rust side builds with Rust 1.94, LTO, codegen-units 1 and jemalloc. The 2022 run on a Xeon E5-1650 v3 showed a 1-CPU win only (41,334 vs 26,700) and gRPC C++ mt ahead at 2-3 CPUs.

## Use it when

- You already run a Thruster app and want a few unary protobuf endpoints served from the same hyper process and middleware chain.
- Small-message unary RPC on 1-2 cores, where the 2026 grpc_bench run puts it at about 1.5-1.8x gRPC C++ req/s with a 11-13 MiB footprint.
- Internal services where you control both ends and the clients send uncompressed unary calls without deadlines.

## Skip it when

- As a general gRPC server: thruster-grpc is unary-only and experimental. It has no streaming, ignores the compression flag and the length prefix, does not enforce grpc-timeout or deadlines, sends no grpc-message, and has no reflection, health or interceptors.
- If you just want a fast Rust gRPC server: tonic (same hyper/h2 base, maintained, full protocol) matched or beat it in the same 2026 run (102,754 vs 98,464 req/s at 1 CPU, 136,638 vs 135,989 at 4 CPUs).
- At 3 or more cores, where the 2022 run had gRPC C++ mt ahead (69,882 vs 56,740 at 2 CPUs) and the 2026 run had Java Vert.x, Scala Pekko and tonic ahead of it.
- Long-lived production code: Thruster's last commit is 2024-10-16, thruster-grpc 0.2.3 dates from 2023-06-26 and is pinned to hyper 0.14/http 0.2, and the README says it has one maintainer and has not been hardened ('Why you shouldn't use Thruster').

## How it is fast

The measured path is hyper 0.14.28 with h2 0.3.26 on tokio (a current_thread runtime for the st build, a multi-thread runtime sized to GRPC_SERVER_CPUS for mt), jemalloc, and prost 0.11 encode and decode. thruster-grpc collects the body, skips the 5-byte gRPC prefix and decodes it, then writes one buffer with the prefix. It does not do the per-call work of the gRPC C++ async API: completion-queue tags, a call-object state machine, deadline and compression handling. Under a 1-CPU docker quota, one event loop with no cross-thread handoff also avoids gRPC core's extra poller threads (our inference from the setup; no source states a mechanism).

## Compared with alternatives

Pick tonic over this for almost any new gRPC service: same hyper/h2 base, full protocol, maintained, and equal or faster in the same runs. Pick grpc-dotnet or grpc-go if you are on those stacks. Choose Thruster only when the gRPC endpoints must live inside an existing Thruster middleware app.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | thruster (feature hyper_server), thruster-grpc 0.2.3 (hyper 0.14, http 0.2, http-body 0.4, prost 0.11, tokio full, tokio-stream, serde, serde_json, lazy_static), prost-build at build time; jemallocator optional (used by the benchmark) |
| **Minimum toolchain** | Stable Rust, edition 2018; no MSRV declared on crates.io. grpc_bench built it with Rust 1.59 (2022) and 1.94 (2026) |
| **Platforms** | Wherever tokio and hyper 0.14 run; not documented further |
| **Thread safety** | The App is committed and shared through an Arc across tokio worker threads; each request gets its own ProtoContext (whose Clone impl panics by design). Nothing else is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness and like-for-like flaw: the Thruster server does less protocol work than gRPC C++. thruster-grpc's get_proto() decodes &body[5..] without checking the compression flag or the declared length, drops body read errors silently (while let Some(Ok(chunk))), and panics on a body shorter than 5 bytes. The benchmark handler also unwrap()s decode errors, so a bad request panics the stream task instead of returning INVALID_ARGUMENT. grpc_bench only counts [OK] replies, so the req/s figures are real, but it is not the same feature set.
- The C++ baseline is weaker than it could be: one outstanding RequestSayHello per completion queue (gRPC's helloworld async example pattern), Debian's prebuilt libgrpc++ (1.51.1 per Debian's tracker; the -O3 -flto flags only reach main.cpp and the stubs), and docker --cpus quotas that also throttle gRPC core's internal threads. So the record's same_opt_level=true is wrong; the verifier's notes say false.
- At 3-4 CPUs the 2026 ratios are capped by the client: the top row (java_vertx_grpc) peaks near 150k req/s and rust_thruster_mt uses only 208-218% of its 300-400% quota, while cpp_grpc_mt burns 306-405% for 81-85k req/s. The gap is partly CPU efficiency, not just peak throughput.
- Responses repeat every response header (content-type, server, grpc-status and a nonstandard 'trailers: grpc-status' header) in the HTTP/2 trailers, and grpc-status is also sent in the initial headers. grpc-go (ghz) accepts it; stricter clients are untested. The benchmark also builds code generated by prost-build 0.14 against the prost 0.11 runtime.

## Known shortcomings

- grpc_bench discussion 559 (2026-04-23): thruster_mt beats cpp_grpc_mt 1.54-1.81x at 1-4 CPUs, but the 2022 wiki run won at 1 CPU only; the C++ side is the Debian distro libgrpc++ (1.51.1, from a search snippet only), so -O3 -flto never reaches gRPC core. The gRPC path is thruster-grpc on hyper/h2, the same stack as tonic. Last commit 2024-10-16.
- Like-for-like flaw: thruster-grpc 0.2.3 (its own README says experimental, about 560 lines) does less work per call than gRPC C++: it decodes &body[5..] without checking the compression flag or length, panics on bodies under 5 bytes, and has no deadlines or streaming; the bench unwrap()s decode errors. The C++ baseline is weak too (one outstanding RequestSayHello per completion queue, Debian prebuilt libgrpc++). At 3-4 CPUs the ghz client tops out near 150k req/s and thruster_mt uses only 208-218% CPU; tonic is equal or faster in the same run. Record correction: same_opt_level true was wrong (the verifier's notes say false).

## Caveats and trade-offs

The Thruster README gives no benchmark numbers, only 'Runs fast'. The measured server is thruster plus the separate thruster-rs/thruster-grpc crate on hyper's HTTP/2 stack and tokio, the same hyper/h2 base as tonic, so the result largely measures hyper/h2 rather than Thruster's own code. In the 2022 run the win was single-CPU only (cpp_grpc_mt led at 2 and 3 CPUs); the 2026 run shows rust_thruster_mt ahead of cpp_grpc_mt at 1-4 CPUs (1.54x to 1.81x), but java_vertx_grpc beats it at 2-4 CPUs and rust_tonic_st beats it at 1 CPU. The C++ baseline is Debian's distro libgrpc++ (1.51.1 per Debian's tracker, a December 2022 release; search snippet only), not an upstream gRPC built with the harness's -O3 -flto, so it is both older and built with distro flags. Server CPU limits use docker --cpus quotas, which penalise gRPC C++'s extra internal threads. Thruster's last commit is 2024-10-16 (stale). [retier] thruster-grpc 0.2.3 (experimental, about 560 lines) does less work per call than gRPC C++: it decodes &body[5..] without checking the compression flag or length, panics on bodies under 5 bytes, and has no deadlines or streaming; the bench unwrap()s decode errors. The C++ baseline posts one outstanding RequestSayHello per completion queue on Debian prebuilt libgrpc++. At 3-4 CPUs the ghz client tops out near 150k req/s and thruster_mt uses only 208-218% CPU; tonic is equal or faster in the same run. same_opt_level is false (the verifier's notes), not true.

Rust middleware web framework; the gRPC server is the separate thruster-grpc crate; the repository's last commit is October 2024.

## Maintenance

Stale: the framework's last commit was 2024-10-16 (two open issues, both from 2023) and thruster-grpc 0.2.3 was last released 2023-06-26 on hyper 0.14; it is MIT and small (thruster-grpc is about 560 lines of Rust), but its own README marks the gRPC layer experimental, so treat it as a curiosity rather than a gRPC C++ replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** Well-known independent shootout (LesnyRumcajs/grpc_bench) with public harness code (rust_thruster_st_bench, rust_thruster_mt_bench, cpp_grpc_st_bench, cpp_grpc_mt_bench Dockerfiles and sources, bench.sh) and stated CPUs for both runs; held at B, as for grpc/grpc in wave 5, because the C++ side links Debian's prebuilt, unpinned libgrpc++ whose build flags and version are not stated by the harness.
- **Retiered** B to C: Enricher: thruster-grpc skips the compression flag and length checks and has no deadlines or streaming, so it does less work per call than the gRPC C++ baseline (itself untuned), and the record's same_opt_level was wrong; unequal-work precedent: B to C.
- **Verifier notes:** Both runs verified; benchmark_url switched to the newer 2026-04-23 discussion, where thruster beats cpp_grpc_mt at 1-4 CPUs (1.54x-1.81x), while the 2022 wiki run shows a 1-CPU-only win. Shortcomings to record: C++ side is Debian's prebuilt libgrpc++ (old 1.51.1, distro flags, unpinned), so same_opt_level is false; Thruster's gRPC path is thruster-grpc on hyper/h2, overlapping tonic's stack; no first-party claim; repo stale. Metadata confirmed: MIT, 1.1k stars, last commit 2024-10-16, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-43 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results>
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/rust_thruster_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/rust_thruster_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/rust_thruster_st_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/rust_thruster_mt_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/rust_thruster_mt_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_grpc_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/HEAD/cpp_asio_grpc_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_thruster_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_thruster_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/rust_thruster_mt_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/14a8435/cpp_grpc_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_mt_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_st_bench/Dockerfile>
  - <https://github.com/thruster-rs/Thruster>
  - <https://github.com/thruster-rs/Thruster/commits>
- **Sources the enricher read:**
  - <https://github.com/LesnyRumcajs/grpc_bench/discussions/559>
  - <https://github.com/LesnyRumcajs/grpc_bench/wiki/2022-04-23-bench-results>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/README.md>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/bench.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/analyze.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/analyze/results_analyze.rb>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/setup_scenario.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/collect_stats.sh>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scenarios/complex_proto/helloworld.proto>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/scenarios/complex_proto/payload>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_st_bench/Cargo.lock>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_st_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_mt_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_mt_bench/Cargo.lock>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_thruster_mt_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_tonic_st_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/rust_tonic_st_bench/src/main.rs>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_mt_bench/main.cpp>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_st_bench/Dockerfile>
  - <https://raw.githubusercontent.com/LesnyRumcajs/grpc_bench/c4c93b3/cpp_grpc_st_bench/main.cpp>
  - <https://crates.io/api/v1/crates/thruster>
  - <https://crates.io/api/v1/crates/thruster-grpc>
  - <https://crates.io/api/v1/crates/thruster-grpc/0.2.3/download>
  - <https://raw.githubusercontent.com/thruster-rs/Thruster/HEAD/README.md>
  - <https://github.com/thruster-rs/Thruster/issues>
  - <https://github.com/thruster-rs/Thruster/commits>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/thruster-rs/thruster`) · [data/wave14/enrich/raw/github_com_thruster_rs_thruster.json](../../../data/wave14/enrich/raw/github_com_thruster_rs_thruster.json) (enrichment confidence 0.6)

</details>
