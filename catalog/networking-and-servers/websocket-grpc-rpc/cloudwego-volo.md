# Volo (CloudWeGo Rust RPC framework)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> CloudWeGo's Rust Thrift/gRPC framework. Self-reports 350k QPS on a 4-core 1KB Thrift echo, about 1.5x Kitex's published pingpong number.

| | |
|---|---|
| **Beats** | Kitex (Go RPC framework implementing Thrift/gRPC protocols) |
| **Claimed result** | "Under the same test conditions as Kitex (limited to 4C), the Volo QPS is 350k; at the same time, we are internally verifying the version based on Monoio ..., and the QPS can reach 440k." |
| **Workload** | Thrift echo RPC, 1KB body, server limited to 4 CPUs (4C), 'same test conditions as Kitex' (cloudwego/kitex-benchmark setup; the in-repo benchmark/scripts/env.sh uses body 1024 and concurrency 100-1000); the README does not say which concurrency the 350k figure comes from |
| **Metric** | throughput |
| **Adoption** | 2.6k stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/cloudwego/volo) · [benchmark](https://github.com/cloudwego/volo#high-performance) |

## Verdict

Volo's README self-reports 350k QPS for a 1KB Thrift echo with the server limited to 4 cores 'under the same test conditions as Kitex' (440k for an unreleased Monoio build), but names no CPU, rustc version, concurrency or connection mode. Kitex's matching 2022 report (Xeon Gold 5118, server 4 CPUs, Go 1.17.2) shows about 228-231k pingpong QPS, which makes Volo about 1.5x (derived from page data), while Kitex-MUX reaches 396-410k at 400-1000 concurrency.

## Use it when

- Writing Thrift RPC services in Rust, especially ones that must call or be called by Kitex (Go) services over TTHeader or Framed Binary.
- Moving a CPU-bound Kitex Thrift service with small (\~1KB) request/response bodies to Rust to raise per-core QPS.
- Services whose governance (timeouts, load balancing including consistent hash, discovery) is written as statically dispatched middleware layers.
- Same-host RPC, where Unix domain sockets or the optional shmipc shared-memory transport (built only on Linux in CI) avoid the TCP loopback path.

## Skip it when

- When you need a published head-to-head benchmark. The README gives only Volo's own QPS, with no CPU, rustc version, concurrency or connection mode and no Kitex number, and the repo has no committed Volo results.
- gRPC-only services chosen for speed: volo-grpc is built on hyper/h2 and has no benchmark of its own.
- When you need registries out of the box: the ROADMAP still lists etcd, ZooKeeper, Nacos, Polaris, Eureka and Consul discovery as not done (issues #71, #475).
- 32-bit targets: volo-thrift pulls in sonic-rs, whose sonic-simd dependency fails on i686, and the maintainers have no plan for 32-bit (issue #543).
- Very high fan-out clients that need a hard connection cap. The Thrift pool Config only has max_idle_per_key (default 10240) and an idle timeout, with no limit on total connections, and one user reported tens of thousands of TIME_WAIT sockets (open issue #641).

## How it is fast

The Thrift path uses a zero-copy codec. The encoder first computes the exact message size and reserves one buffer. It then splices large Bytes/FastStr fields into a LinkedBytes chain (the recommended threshold is 4KB) and flushes it with vectored writes (writev), while the decoder hands out Bytes::split_to slices of the read buffer instead of copying. An opt-in unsafe-codec feature switches to Pilota's unchecked binary protocol, and the in-repo benchmark turns it on. Static dispatch through AFIT/RPITIT middleware, per-connection Tokio tasks with pooled client connections, and a release profile with lto=true and codegen-units=1 keep framework overhead low; the README says it is 'basically negligible (excluding syscall overhead)' in production flame graphs.

## Compared with alternatives

Pick Volo over Kitex when you want Rust and about 1.5x Kitex's pingpong QPS (Volo's 350k vs Kitex's published \~229k) while you stay wire-compatible with a Kitex/TTHeader fleet; Kitex-MUX's 396-410k is still higher. Pick it over SRPC or brpc when the stack is Rust rather than C++. For gRPC-only Rust servers, wtx has a direct grpc-go comparison and Volo does not.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio, motore, pilota (IDL codegen and codec), metainfo, faststr, linkedbytes, socket2, nix, libc. volo-thrift adds sonic-rs; volo-grpc adds hyper 1.x, h2 and tower (tonic/tonic-web only for the optional grpc-web feature). TLS is optional via rustls (aws-lc-rs or ring) or native-tls, and shmipc is optional. |
| **Minimum toolchain** | Rust 1.85.0 stable (workspace rust-version, edition 2024); CI tests on stable and nightly |
| **Platforms** | Linux x86-64 is fully tested in CI. Linux aarch64, macOS and Windows are build/clippy-checked only (--no-test), and macOS and Windows are checked without shmipc. 32-bit x86 does not build (issue #543). |
| **Thread safety** | Clients are Clone and shared across tasks (the benchmark clones one client across workers). #[volo::main] is a re-export of tokio::main, and the server spawns one Tokio task per accepted connection. |
| **Drop-in for the baseline** | partial — wire-compatible with Kitex (Thrift Binary/Compact over Framed or TTHeader), so the two can call each other, but services must be rewritten in Rust from the same IDL |

## Gotchas

- The default codec is TTHeader&lt;Framed&lt;Binary&gt;&gt;, and TTHeader is a CloudWeGo-private header that only Volo and Kitex understand. Clients calling plain Apache Thrift servers need DefaultMakeCodec::framed() or ::buffered(). Servers auto-detect TTHeader, Framed, and Binary/Compact/FBThrift-compact, and the default max frame size is 16MB.
- unsafe-codec (the benchmark build uses it) 'may cause undefined behavior if the thrift message is malformed'. unsafe_unchecked swaps unreachable!() for unreachable_unchecked. Keep both off on endpoints that receive untrusted input.
- Multiplexing is behind the 'multiplex' feature, off by default, and documented as unstable with no backward-compatibility promise. The in-repo benchmark compiles it in but runs a pingpong pooled client with the Framed codec.
- The 440k QPS figure is a Monoio-based internal build. The published crates are Tokio-only (monoio is not a workspace dependency), so expect the 350k-class number at most.

## Known shortcomings

- Self-reported 2022 numbers only: no CPU, rustc version, concurrency, connection mode or Kitex number, and no Volo results in the repo. The in-repo benchmark appears to be pingpong with a pooled client, so the fair Kitex comparison is Kitex pingpong (\~229k, \~1.5x derived), not Kitex-MUX (396-410k, which beats Volo); the README never confirms it. The benchmark build enables unsafe-codec, which its docs say may cause UB on malformed Thrift messages, so the numbers may not reflect the safe default. The 440k Monoio build is unreleased (shipped crates are Tokio-only). No cap on client connections (only max_idle_per_key 10240 and idle timeout); #641 reports tens of thousands of TIME_WAIT sockets. No 32-bit x86 build (sonic-rs, #543); only Linux x86-64 fully tested. Pre-1.0 crates; registry integrations unfinished; volo-grpc has no benchmark. Default TTHeader&lt;Framed&lt;Binary&gt;&gt; codec is CloudWeGo-private (plain Apache Thrift servers need framed() or buffered()).

## Caveats and trade-offs

The README hedges the comparison itself: "it is very unfair to compare the performance with the Go framework, so we will not focus on comparing the performance of Volo and Kitex ... I hope everyone can view it objectively" and "we'll only publish our own QPS data." The page gives no Kitex number. Kitex's figures under the matching setup are in cloudwego/kitex-benchmark scripts/reports/thrift.csv (last updated 2022-08-26; Xeon Gold 5118, server 4 CPUs, 1KB echo, Go 1.17.2). There Kitex does about 228-231k QPS, so Volo's 350k is about 1.5x (derived from page data). But Kitex-MUX reaches 396-410k at 400-1000 concurrency, above Volo's 350k, and the README does not say which connection mode or concurrency Volo used. The 440k Monoio figure is an unreleased internal build. The High Performance text dates from 2022-08-23 and has not been re-run since. No CPU model, rustc version or flags are stated for the Volo run. The in-repo benchmark (benchmark/scripts) covers Volo only, with no Kitex harness. GitHub detects only Apache-2.0, but the README and Cargo.toml say MIT OR Apache-2.0 (LICENSE-MIT and LICENSE-APACHE both present). The baseline is Kitex (Go), which is itself cataloged, not a C++ incumbent.

Rust vs. Go (Kitex); Volo implements both Thrift (volo-thrift) and gRPC (volo-grpc) protocols itself rather than replacing a generic incumbent wholesale; a separate Monoio-runtime-based variant is described as still 'internally verifying' (not the shipped default).

## Maintenance

Actively maintained (last main commit 2026-08-31, volo-thrift 0.12.6 on crates.io with about 485k total downloads) and dual-licensed MIT OR Apache-2.0, but every crate is pre-1.0 and the performance text dates from 2022 and has not been re-run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party Volo QPS only (350k, 440k Monoio-based internal build) 'under the same test conditions as Kitex (limited to 4C)', with no Kitex number, CPU model, rustc version or flags. The in-repo benchmark/scripts (bench.sh, env.sh, build.sh; 1KB Thrift echo, server pinned to 4 CPUs, concurrency 100-1000, cargo --release --features unsafe-codec) match the kitex-benchmark setup, but no hardware or toolchain is stated for the Volo run, so this is C, not A.
- **Verifier notes:** The claimed_speedup quote matches the README word for word. Treat the page as an implicit comparison: it names Kitex's test conditions but declines to give Kitex numbers. Last commit on main is 2026-08-31 (the record's 2026-09-23 is pushedAt, from another branch). Stars 2,626, not archived, not a fork. GitHub REST was rate-limited, so metadata came from GraphQL.
- **Fields the verifier corrected:** `last_commit`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cloudwego/volo#high-performance>
  - <https://github.com/cloudwego/volo>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/README.md>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/benchmark/scripts/bench.sh>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/benchmark/scripts/env.sh>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/benchmark/scripts/build.sh>
  - <https://raw.githubusercontent.com/cloudwego/kitex-benchmark/main/README.md>
  - <https://raw.githubusercontent.com/cloudwego/kitex-benchmark/main/scripts/reports/thrift.csv>
  - <https://www.cloudwego.io/docs/volo/overview/>
- **Sources the enricher read:**
  - <https://github.com/cloudwego/volo>
  - <https://github.com/cloudwego/volo#high-performance>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/README.md>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/Cargo.toml>
  - <https://github.com/cloudwego/volo/blob/main/ROADMAP.md>
  - <https://github.com/cloudwego/volo/blob/main/SECURITY.md>
  - <https://github.com/cloudwego/volo/blob/main/volo/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo/src/lib.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo/src/net/mod.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo/src/macros.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-macros/src/lib.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/Cargo.toml>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/README.md>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/src/lib.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/src/codec/mod.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/src/codec/default/mod.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/src/codec/default/thrift.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo-thrift/src/codec/default/ttheader.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo-thrift/src/codec/default/framed.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-thrift/src/transport/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo-thrift/src/transport/pool/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo-thrift/src/client/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/volo-thrift/src/server/mod.rs>
  - <https://github.com/cloudwego/volo/blob/main/volo-grpc/Cargo.toml>
  - <https://github.com/cloudwego/volo/blob/main/benchmark/Cargo.toml>
  - <https://github.com/cloudwego/volo/blob/main/benchmark/src/bin/client.rs>
  - <https://github.com/cloudwego/volo/blob/main/benchmark/src/bin/server.rs>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/benchmark/scripts/bench.sh>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/benchmark/scripts/env.sh>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/benchmark/scripts/build.sh>
  - <https://raw.githubusercontent.com/cloudwego/volo/main/.github/workflows/ci.yaml>
  - <https://github.com/cloudwego/volo/issues>
  - <https://github.com/cloudwego/volo/issues/641>
  - <https://github.com/cloudwego/volo/issues/543>
  - <https://github.com/cloudwego/volo/issues/652>
  - <https://github.com/cloudwego/volo/issues/554>
  - <https://www.cloudwego.io/docs/volo/overview/>
  - <https://www.cloudwego.io/docs/volo/volo-thrift/getting-started/>
  - <https://crates.io/api/v1/crates/volo>
  - <https://crates.io/api/v1/crates/volo-thrift>
  - <https://crates.io/api/v1/crates/volo-grpc>
  - <https://hn.algolia.com/api/v1/items/47832132>
  - <https://raw.githubusercontent.com/cloudwego/kitex-benchmark/main/README.md>
  - <https://raw.githubusercontent.com/cloudwego/kitex-benchmark/main/scripts/reports/thrift.csv>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cloudwego/volo`) · [data/wave5/enrich/raw/github_com_cloudwego_volo.json](../../../data/wave5/enrich/raw/github_com_cloudwego_volo.json) (enrichment confidence 0.7)

</details>
