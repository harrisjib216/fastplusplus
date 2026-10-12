# TQUIC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Tencent's Rust QUIC/HTTP3 library with C API: \~2.4x quiche on request and stream-churn rate, slower on bulk.

| | |
|---|---|
| **Beats** | quiche |
| **Claimed result** | \~2.4x quiche on request/message-rate scenarios (p50, syscall backend, derived from page data): request/response 155,043 vs 64,574 rps (2.40x), stream churn 178,272 vs 74,756 streams/s (2.38x), small-payload messages 176,604 vs 73,852 msgs/s (2.39x), 0-RTT request/response 154,448 vs 65,327 rps (2.36x), close/reset cleanup 178,364 vs 75,080 streams/s (2.38x); io_uring backend 3.0-3.4x. In the same run TQUIC is slower than quiche on every bulk-throughput row (download 8.600 vs 11.258 Gbps; 0.76-0.96x across download, upload, bidirectional, multistream, loss-recovery and flow-control, syscall), on resumed connect (216 vs 301 conn/s, 0.72x) and on DATAGRAM rate (0.17x). |
| **Workload** | quicperf: same shared C++ harness as the ngtcp2 entry, loopback UDP, CUBIC, shared TLS 1.3 Ed25519 material, one pinned server thread. The rows measure fresh-stream request/response rate, stream churn (open/send/receive/finish), tiny-message rate, 0-RTT request/response and close/reset cleanup, all with 16 client threads. A saturation scout chose the thread count; the published p50s come from 20 fixed randomized-block samples per row, with scout samples excluded. |
| **Metric** | throughput |
| **Compiler and flags** | TQUIC pinned to commit 50f5a55 (2025-09-11, head of Tencent/tquic branch feature/support_datagram_extension_t2, not a tagged release) and built via depofiles/tquic.DepoFile: RUSTFLAGS="-C target-cpu=native -C opt-level=3", CARGO_PROFILE_RELEASE_LTO=fat, CARGO_PROFILE_RELEASE_CODEGEN_UNITS=1, --no-default-features --features ffi, linked against quicperf's BoringSSL (main-beddb58, via BORINGSSL_LIB_DIR). quiche 0.29.0 (commit e85fc8e) was built with the same RUSTFLAGS and LTO settings. The C++ harness uses CMake Release, -O3, native CPU flags and LTO by default. |
| **Adoption** | 1438 stars |
| **Last commit** | 2025-12-23 |
| **Links** | [repository](https://github.com/Tencent/tquic) · [benchmark](https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md) |

## Verdict

quicperf is an independent C++ loopback harness: one pinned server thread, 16 client threads, CUBIC, TLS 1.3 through a shared BoringSSL build, p50 of 20 samples. In it, TQUIC at feature-branch commit 50f5a55 reached 2.36-2.40x quiche 0.29.0 on request/response, stream churn, small messages, 0-RTT and close/reset with the syscall backend. With io_uring the ratio was 3.0-3.4x, partly because quiche's own io_uring rows are slower than its syscall rows. TQUIC lost on every bulk row (0.76-0.96x), on resumed connect (0.72x) and on DATAGRAM rate (0.17x). Both libraries were built with -C target-cpu=native -C opt-level=3 and fat LTO; the CPU model is not recorded and the run came from a harness working tree with uncommitted changes.

## Use it when

- Single-threaded QUIC servers that handle many small request/response exchanges on fresh streams. quicperf measured 155k rps for TQUIC vs 119k for LSQUIC and 64.6k for quiche on one pinned server thread.
- Workloads that open and close many short streams, such as RPC-style stream churn or close/reset cleanup: about 178k streams/s vs about 75k for quiche.
- High-rate 0-RTT request/response after session resumption: 154k vs 65k rps for quiche.
- You want a Rust QUIC stack with a C API that already handles CID routing, per-connection timers and send batching, so you don't have to write that code around quiche.
- You need Multipath QUIC, BBRv3/COPA, or mobile targets (Android, iOS and HarmonyOS builds are documented).

## Skip it when

- Bulk transfer. In the same run TQUIC downloaded at 8.6 Gbps vs quiche 11.3, LSQUIC 16.4 and ngtcp2 18.2 Gbps, and it lost to quiche on every upload, bidirectional, multistream, loss-recovery and flow-control row (0.76-0.96x).
- Unreliable DATAGRAMs (RFC 9221). They are not in develop or release v1.6.0 (issue #222 still open) and exist only on feature branches. Even the feature-branch build managed 0.89M vs 5.1M DATAGRAMs/s for quiche.
- Workloads dominated by resumed connections: 216 vs 301 conn/s for quiche (syscall backend).
- Memory-tight servers holding many idle connections: 146.6 KB vs 125.4 KB of RSS per idle connection compared with quiche (syscall). Issue #494 (tquic_server OOM-killed while serving a 30 MB file) is still open, and its fix PR #498 was closed without merging.
- Full HTTP/3 feature coverage. The QPACK dynamic table is a TODO in qpack.rs (#225), and ECN (#224), QUIC v2 (#221), HTTP/3 trailers (#226) and async APIs (#23) are missing.

## How it is fast

Connections live in a slab indexed through FxHash CID routing tables. Each process_connections pass touches only connections marked 'tickable', meaning they have pending events. It then round-robins over 'sendable' connections and writes packets into a reusable buffer pool. Those packets go to the application's send callback in batches (send_batch_size, default 64), which fits sendmmsg-style I/O. Timers for all connections share one double-ended priority queue, and streams use FxHashMap indexes, bitflag state and per-urgency send queues. Neither TQUIC nor quicperf says which of these explains the \~2.4x request-rate gap over quiche, so the cause is not documented. The design shows no advantage on bulk-transfer paths.

## Compared with alternatives

Pick TQUIC over ngtcp2, LSQUIC or picoquic when one server thread must handle as many small requests or short streams as possible. In the same quicperf run it served 155k rps vs 119k for LSQUIC, 59k for picoquic and 51k for ngtcp2. Pick ngtcp2 or LSQUIC for bulk throughput (about 2x TQUIC's download rate), and quiche for DATAGRAM rate or resumed connects.

## Integration

| | |
|---|---|
| **Form** | crate; also static lib and shared lib (crate-type lib/staticlib/cdylib, C API enabled with --features ffi, header include/tquic.h) |
| **Dependencies** | BoringSSL (vendored git submodule built via CMake, or a prebuilt one via BORINGSSL_LIB_DIR); Rust crates ring, bytes, slab, rustc-hash, priority-queue, smallvec, lru, brotli, flate2 and others; optional serde (qlog feature) and sfv (h3 feature) |
| **Minimum toolchain** | Rust 1.70 (Cargo rust-version), but the repo pins 1.90.0 in rust-toolchain.toml after recent toolchain breakages; the docs also require GCC 9.3+, CMake 3.22+ and git 2.0+ |
| **Platforms** | Linux, macOS, FreeBSD, Windows, iOS, Android and HarmonyOS per the docs; open issues report no exported C symbols in the Windows static lib (#484) and a build failure on Apple M1 (#447) |
| **Thread safety** | Not documented. In Rust the Endpoint holds Rc&lt;RefCell&lt;..&gt;&gt; and Rc&lt;dyn PacketSendHandler&gt;, which makes it !Send. Treat each endpoint as confined to one thread and scale with one endpoint per thread/core. The FFI adds no locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- A packet-generation error on one connection makes process_connections return Err for the whole endpoint, and the remaining connections are not processed on that pass. Issue #459 reports repeated InternalError under 1.5-2 Gbps load.
- The library does no GSO or sendmmsg itself. Each outgoing packet is a separate Vec&lt;u8&gt; in the batch handed to on_packets_send, so the batching only pays off if your callback does vectored or segmented sends.
- tquic.h #includes openssl/ssl.h and exposes SSL_CTX (quic_tls_config_new_with_ssl_ctx). C/C++ consumers need BoringSSL headers and must link the same BoringSSL build as TQUIC.
- The benchmarked build (50f5a55) is a DATAGRAM feature-branch commit, 1 ahead of and 3 behind develop. The published crate (v1.6.0, Feb 2025) cannot reproduce the DATAGRAM rows. quic_set_logger at TRACE level is reported to crash (#500).

## Known shortcomings

- Request/response and small-message wins only (\~2.4x); slower than quiche on every bulk-throughput row (0.76-0.96x), resumed connect (0.72x) and datagram rate (0.17x). Measured at a feature-branch commit, not a release, in a small personal harness with no CPU model.
- The benchmarked commit is on a DATAGRAM feature branch not in any release; last release v1.6.0 (2025-02). Open bugs: server OOM-killed serving a 30 MB file (#494), one bad packet fails process_connections for the whole endpoint under load (#459), TRACE logging crash (#500). No QPACK dynamic table, ECN or QUIC v2; idle memory per connection higher than quiche; C users must link the same BoringSSL build.

## Caveats and trade-offs

quicperf (victorstewart/quicperf, 27 stars) is an independent but small personal harness. Its committed environment file (docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt) and adaptive-samples.tsv record only an anonymized machine_hash, with no CPU model, so it is Tier C, not A or B. The benchmark is loopback-only. The 2026-06-01 run came from a dirty working tree (uncommitted edits to perf.tquic.h, perf.quiche.h and other adapters on top of commit 3eda036). TQUIC was measured at a feature-branch commit, not a release. The win is limited to request, stream and message rate: TQUIC loses to quiche on every bulk-throughput scenario in the same run. TQUIC's own first-party benchmark (https://tquic.net/docs/further_readings/benchmark; AMD EPYC 7K62, Linux 4.14, 'release mode', single-threaded servers, HTTP/3) does include Cloudflare quiche (QUICHE-CF v0.18.0), alongside QUICHE-G v118, NGINX-QUIC 1.25.2 and LSQUIC 4.0.1. It claims 'four to five times faster' than QUICHE-G and 'up to 20%' faster than LSQUIC, but gives charts only (no raw numbers, no compiler flags). Read approximately from the charts, TQUIC is about 1.2-1.5x QUICHE-CF on long connections and about 9x on 1 KB short connections. That page is first-party Tier C and is not the primary evidence here.

Implemented in Rust (exposes C/C++ FFI, not a native C++ library). In the same harness TQUIC loses to quiche on raw bulk download throughput (8.6-8.9 vs 9.8-11.3 Gbps) and on resumed-connection rate (216 vs 306 conn/s, syscall), so its measured edge is specific to request/response and stream-churn rate, not bulk transfer.

## Maintenance

Apache-2.0 (includes BSD/MIT-derived code) and usable as a vendored crate or static lib. Despite the 'active' label, there has been no release since v1.6.0 (2025-02-25), and develop has seen only toolchain fixes since August 2025 (last commit 2025-12-23).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** latest-results.md compares TQUIC and quiche side by side in one harness, and all eight cited p50 numbers match their rows; pairwise-comparisons.tsv confirms each ratio with tight 95% CIs (for example reqresp syscall quiche/TQUIC 0.416 [0.406-0.421]). The code is public (perf.tquic.h, perf.quiche.h, depofiles/) and flags are stated, but no CPU model is recorded, so it is not A. quicperf is a small personal harness (27 stars), not a well-known independent suite, so it is not B. TQUIC's own tquic.net benchmark is first-party, gives charts only and states no compiler flags, so it is also C.
- **Verifier notes:** Downgraded from B to C for the obscure-harness and no-CPU rule, and the claimed range corrected: all four cited ratios are 2.36-2.40x, not 2.1-2.4x. The original caveat was wrong that TQUIC's own benchmark omits Cloudflare quiche (QUICHE-CF v0.18.0 is in it). GitHub reports the license as NOASSERTION, but LICENSE says TQUIC is Apache-2.0, with derived quiche (BSD-2), Chromium (BSD-3) and quinn (MIT) code, so Apache-2.0/copyable stands. Other metadata checks out: 1438 stars, not a fork, not archived, last commit 2025-12-23, active. The record's tradeoffs field (not correctable here) quotes resumed connect as 216 vs 306 'syscall'; 306 is quiche's io_uring row, and its syscall row is 301.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/pairwise-comparisons.tsv>
  - <https://raw.githubusercontent.com/victorstewart/quicperf/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/adaptive-samples.tsv>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/tquic.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/quiche.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/3eda036a66524d9375befb5e80fa61aa39a19d06/depofiles/tquic.DepoFile>
  - <https://github.com/Tencent/tquic>
  - <https://github.com/Tencent/tquic/commits>
  - <https://github.com/Tencent/tquic/blob/develop/LICENSE>
  - <https://github.com/Tencent/tquic/blob/develop/README.md>
  - <https://github.com/Tencent/tquic/tree/develop/benches>
  - <https://github.com/Tencent/tquic/commit/50f5a55975fe5b64cce708bbf227dd0f29b59ee5>
  - <https://github.com/Tencent/tquic/releases>
  - <https://tquic.net/docs/further_readings/benchmark>
  - <https://tquic.net/assets/images/benchmark_long_15k-98da5bce63503f580dc9062904c02449.png>
  - <https://tquic.net/assets/images/benchmark_long_50k-c35679ad3c272a4e614a43acf93dcd18.png>
  - <https://tquic.net/assets/images/benchmark_long_2m-7b86a9004fefa8b5ffcfee57c76f549a.png>
  - <https://tquic.net/assets/images/benchmark_short-00af76da7acc46fe38b59de75c08aa9f.png>
- **Sources the enricher read:**
  - <https://github.com/Tencent/tquic>
  - <https://github.com/Tencent/tquic/blob/develop/README.md>
  - <https://github.com/Tencent/tquic/blob/develop/Cargo.toml>
  - <https://github.com/Tencent/tquic/blob/develop/rust-toolchain.toml>
  - <https://github.com/Tencent/tquic/blob/develop/include/tquic.h>
  - <https://github.com/Tencent/tquic/blob/develop/src/lib.rs>
  - <https://github.com/Tencent/tquic/blob/develop/src/endpoint.rs>
  - <https://github.com/Tencent/tquic/blob/develop/src/build.rs>
  - <https://github.com/Tencent/tquic/blob/develop/src/ffi.rs>
  - <https://github.com/Tencent/tquic/blob/develop/src/connection/stream.rs>
  - <https://github.com/Tencent/tquic/blob/develop/src/timer_queue.rs>
  - <https://github.com/Tencent/tquic/blob/develop/src/h3/qpack/qpack.rs>
  - <https://github.com/Tencent/tquic/blob/develop/CHANGELOG.md>
  - <https://github.com/Tencent/tquic/blob/develop/ADOPTERS.md>
  - <https://github.com/Tencent/tquic/branches>
  - <https://github.com/Tencent/tquic/releases>
  - <https://github.com/Tencent/tquic/commits/develop>
  - <https://github.com/Tencent/tquic/compare/develop...50f5a55975fe5b64cce708bbf227dd0f29b59ee5>
  - <https://github.com/Tencent/tquic/issues>
  - <https://github.com/Tencent/tquic/issues/494>
  - <https://github.com/Tencent/tquic/issues/516>
  - <https://github.com/Tencent/tquic/issues/459>
  - <https://github.com/Tencent/tquic/issues/512>
  - <https://github.com/Tencent/tquic/issues/499>
  - <https://github.com/Tencent/tquic/pull/498>
  - <https://crates.io/api/v1/crates/tquic>
  - <https://tquic.net/docs/getting_started/installation>
  - <https://tquic.net/docs/further_readings/benchmark>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.tquic.h>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/tquic.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/tencent/tquic`) · [data/wave5/enrich/raw/github_com_tencent_tquic.json](../../../data/wave5/enrich/raw/github_com_tencent_tquic.json) (enrichment confidence 0.72)

</details>
