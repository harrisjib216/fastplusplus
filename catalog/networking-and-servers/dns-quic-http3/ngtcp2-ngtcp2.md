# ngtcp2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Pure-C IETF QUIC transport library (RFC 9000); in one loopback harness, 1.5-2.1x quiche's bulk-transfer throughput.

| | |
|---|---|
| **Beats** | quiche |
| **Claimed result** | \~1.5-2.1x quiche on bulk-transfer scenarios (p50, syscall backend, derived from page data): download 18.227 vs 11.258 Gbps (1.62x), upload 31.047 vs 14.794 Gbps (2.10x), bidirectional 20.503 vs 12.662 Gbps (1.62x), multistream download 16.459 vs 10.990 Gbps (1.50x), multistream upload 24.816 vs 15.291 Gbps (1.62x), loss-recovery 17.379 vs 11.689 Gbps (1.49x), flow-control 15.600 vs 10.309 Gbps (1.51x); io_uring backend 1.35-1.71x. In the same run ngtcp2 is slower than quiche on request/response (0.80x), stream churn (0.70x), small-payload messages (0.71x), 0-RTT request/response (0.70x), close/reset cleanup (0.70x), connect (0.41x), resumed connect (0.37x) and DATAGRAM rate (0.29x), all syscall. |
| **Workload** | quicperf: an apples-to-apples C++ benchmark harness running the same shared TLS material, saturation policy, and socket backend (syscall/io_uring) against native adapters for ngtcp2, LSQUIC, TQUIC, quiche, picoquic, XQUIC and several Rust/Zig stacks, over loopback UDP with CUBIC congestion control. Scenarios include bulk download/upload, bidirectional transfer, multistream transfer, loss recovery, and flow-control-limited transfer. |
| **Metric** | throughput |
| **Compiler and flags** | quicperf C++ harness: CMake Release, -O3, native CPU flags, LTO by default (per README). ngtcp2 1.22.1 built from the release tarball via depofiles/ngtcp2.DepoFile (CMake, static, BoringSSL main-beddb58 backend); that depofile sets no extra optimisation flags of its own. quiche 0.29.0 (cloudflare/quiche commit e85fc8e) built via depofiles/quiche.DepoFile with RUSTFLAGS="-C target-cpu=native -C opt-level=3", CARGO_PROFILE_RELEASE_LTO=fat, CARGO_PROFILE_RELEASE_CODEGEN_UNITS=1, --features ffi. |
| **Adoption** | 1521 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/ngtcp2/ngtcp2) · [benchmark](https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md) |

## Verdict

The run is victorstewart/quicperf's 2026-06-01 Linux loopback matrix. It used CUBIC for every library, one shared C++ harness with sendmmsg/GSO batching, -O3/native/LTO builds, ngtcp2 1.22.1 on BoringSSL and quiche 0.29.0 with fat LTO; the CPU model is not recorded and the tree was dirty. ngtcp2's p50 bulk throughput was 1.49-2.10x quiche's on the syscall backend (e.g. upload 31.0 vs 14.8 Gbps) and 1.35-1.71x on io_uring. In the same run it was 0.29-0.80x quiche on connect, request/response, stream-churn and DATAGRAM rates.

## Use it when

- Sustained bulk transfer (large downloads or uploads, several streams, or both directions at once): in quicperf it had the best p50 of all libraries on download, bidirectional (20.5 Gbps), multistream download and upload, and flow-control-limited rows.
- C or C++ servers and clients that already own their event loop (epoll, io_uring, libev) and want a transport core with no external library dependencies.
- Projects that must choose their TLS stack: BoringSSL/aws-lc, GnuTLS, wolfSSL, Picotls, LibreSSL, or OpenSSL &gt;= 3.5 (experimental).
- HTTP/3 clients built on nghttp3. curl documents ngtcp2 as its only non-experimental HTTP/3 backend; quiche is marked EXPERIMENTAL there.
- Servers holding many mostly-idle connections: the run's lowest idle-footprint row was ngtcp2 over io_uring at about 76.5 KB per connection.

## Skip it when

- Connection-setup-heavy workloads: 113 vs 277 conn/s for quiche on fresh connects (0.41x) and 112 vs 301 on resumed connects (0.37x) in the same run.
- Small request/response, stream churn or small-message rate: 51k vs 65k rps for quiche (0.80x). TQUIC (155k) and LSQUIC (119k) are far ahead in the same run.
- High-rate unreliable DATAGRAM traffic: 1.50M vs 5.14M datagrams/s for quiche (0.29x).
- Multipath QUIC: not supported (see open roadmap issue #2318).
- Teams wanting a batteries-included stack: sockets, timers, pacing, CID-to-connection routing and TLS setup are all application code, and HTTP/3 needs a second library (nghttp3).

## How it is fast

Neither upstream nor the benchmark attributes the gap to a specific mechanism. The source shows copy-avoidance on both sides. In-order stream data goes to the recv_stream_data callback straight from the decrypted packet buffer, and only out-of-order data is copied into a reorder buffer (ngtcp2_rob). Outgoing stream data is borrowed from the application via ngtcp2_vec until acked_stream_data_offset fires, not copied into an internal send buffer. Internally it uses a deterministic paged skip list (ngtcp2_ksl), a Robin Hood open-addressing hash map with Fibonacci hashing (ngtcp2_map), and an object pool on a block allocator (ngtcp2_objalloc) to cut small-object malloc cost. In quicperf, sendmmsg and GSO batching live in the harness's shared C++ path for every library, so the measured gap reflects per-packet library cost, not socket I/O.

## Compared with alternatives

Pick ngtcp2 over quiche, picoquic, TQUIC and LSQUIC when multi-stream or bidirectional bulk throughput dominates. In the same quicperf run it beat LSQUIC's collapsed bidirectional and multistream rows (20.5 vs 2.1 Gbps bidirectional), though LSQUIC edged it on single-stream upload (33.5 vs 31.0 Gbps) and loss recovery (18.3 vs 17.4 Gbps). Choose TQUIC or LSQUIC for request/message rate, and picoquic or quic-zig for connection-setup rate.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | none for libngtcp2 itself. The crypto helper needs one TLS stack: BoringSSL/aws-lc, GnuTLS &gt;= 3.7.5, wolfSSL &gt;= 5.5.0, Picotls (pinned commit), LibreSSL &gt;= 3.9.2, quictls (deprecated) or OpenSSL &gt;= 3.5.0 (experimental). HTTP/3 needs nghttp3. The examples also need libev. |
| **Minimum toolchain** | C11. README lists clang &gt;= 19, gcc &gt;= 15 and MSVC 2022 (1944) as known to work. Build with CMake &gt;= 3.20, or autotools plus pkg-config &gt;= 0.20. Only the examples need C++23. |
| **Platforms** | Upstream CI covers Linux x86-64 and arm64, macOS, Windows x86/x64 (MSVC via vcpkg) and MinGW x86_64/i686 cross builds. No ISA-specific requirement is documented. |
| **Thread safety** | ngtcp2_conn is not thread-safe (maintainer, issue #1029): drive each connection from one thread or add your own locking. ngtcp2_rand_ctx allows a per-thread or per-connection RNG. |
| **Drop-in for the baseline** | no |

## Gotchas

- Pacing is the application's job: call ngtcp2_conn_update_pkt_tx_time() after writing (ngtcp2_conn_write_aggregate_pkt() does this for you) and honor ngtcp2_conn_get_expiry2(). quicperf's ngtcp2 adapter never calls it, and its quiche adapter ignores send_info pacing, so the published numbers are unpaced.
- The outgoing UDP payload is 1200 bytes by default and grows only through PMTUD. The benchmark turned PMTUD off and set no_tx_udp_payload_size_shaping=1 with a 1452-byte max_tx_udp_payload_size; stock settings will not match its numbers.
- Send buffers are borrowed: memory passed to ngtcp2_conn_writev_stream() must stay valid until acked_stream_data_offset reports it acknowledged. If the server rejects 0-RTT data, the library does not resend it as 1-RTT; the application must reopen streams and write the data again.
- Two high-severity CVEs were buffer overflows in the qlog code: CVE-2024-52811 (1.9.0, fixed in 1.9.1) and CVE-2026-40170 (&lt;= 1.22.0, fixed in 1.22.1). Use &gt;= 1.22.1 if you enable qlog.

## Known shortcomings

- Bulk-transfer only: in the same quicperf run ngtcp2 is slower than quiche on request/response, stream churn, small messages, 0-RTT, connect (0.41x), resumed connect and datagram rate. quicperf is a small personal harness with no CPU model, and the run came from a dirty working tree with uncommitted adapter edits.
- quicperf ran ngtcp2 and quiche unpaced (no ngtcp2_conn_update_pkt_tx_time; quiche's send_info.at ignored) and ngtcp2 with non-default settings (PMTUD off, payload shaping off, 1452-byte payload vs the 1200-byte default). Nobody explains why it is faster; batching is shared harness code. Benchmarked 1.22.1, upstream is 1.25.0. Two high-severity qlog CVEs (CVE-2024-52811, CVE-2026-40170, fixed in 1.22.1). ngtcp2_conn is not thread-safe (stated only in issue #1029). No multipath QUIC (#2318). LSQUIC beats it on upload-syscall and loss-recovery rows in the same run.

## Caveats and trade-offs

quicperf (victorstewart/quicperf, 27 stars) is an independent but small personal harness. Its committed run-environment file (docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt) and adaptive-samples.tsv record only an anonymized machine_hash, with no CPU model, so hardware is not stated. That rules out Tier A, and the harness is not well known enough for B. The benchmark is loopback-only, with no physical or WAN link. The 2026-06-01 run was taken from a dirty working tree: the environment file's git status shows uncommitted edits to perf.ngtcp2.h, perf.quiche.h, perf.cpp and other adapters on top of commit 3eda036, so the committed code may not reproduce it exactly. The syscall download row (both libraries) and quiche's syscall bidirectional row are flagged 'inconclusive'. The publishable-only pairwise-comparisons.tsv still shows ngtcp2 winning upload, multistream, loss-recovery and flow-control rows at 1.35-2.10x. The win is limited to bulk transfer: ngtcp2 loses to quiche on every connection-setup and small-request scenario in the same run.

C library requiring an external TLS backend (OpenSSL/BoringSSL/GnuTLS/wolfSSL/picotls) and manual event-loop integration, unlike quiche's more batteries-included Rust API. In the same quicperf harness ngtcp2 is markedly slower than quiche and most peers on connection-establishment rate (113 vs 277 conn/s, syscall) and on plain request/response rate (51,386 vs 64,574 rps), so its measured advantage is specific to sustained bulk-transfer throughput, not connection setup or small-request rate.

## Maintenance

Actively maintained (push on 2026-09-26, roughly monthly releases up to v1.25.0 on 2026-07-26, one open issue), MIT-licensed, and fuzzed and sanitizer-tested in CI; the benchmarked 1.22.1 is three minor releases behind, but its structs and functions are versioned (e.g. \*_versioned entry points) to keep the ABI stable across releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** latest-results.md compares ngtcp2 and quiche side by side in one harness, and all twelve cited p50 numbers match their rows; pairwise-comparisons.tsv confirms the publishable wins with 95% CIs (upload syscall 2.10x [2.06-2.11]). The harness code is public (perf.ngtcp2.h, perf.quiche.h, depofiles/) and flags are stated, but no CPU model is recorded, so it is not A; quicperf is a small personal harness (victorstewart/quicperf, 27 stars), not a well-known independent suite, so it is not B either (same rule applied earlier to chronoxor/CppSerialization, bemayer/xml-benchmark and prng-test-bench).
- **Verifier notes:** Downgraded from B to C for the obscure-harness and no-CPU rule, and the low end of the claimed range corrected (loss recovery 1.49x and flow control 1.51x are below 1.6x). Metadata checks out: MIT, 1521 stars, not a fork, not archived, last commit 2026-09-26, active. The record's tradeoffs field already notes the connect and request-rate losses.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/tree/main/docs/results/fixed-full-matrix-max16-20260601T175816Z>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-run-summary.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/pairwise-comparisons.tsv>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/publication-results.tsv>
  - <https://raw.githubusercontent.com/victorstewart/quicperf/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/adaptive-samples.tsv>
  - <https://github.com/victorstewart/quicperf/tree/main/depofiles>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/ngtcp2.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/quiche.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/3eda036a66524d9375befb5e80fa61aa39a19d06/depofiles/ngtcp2.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/3eda036a66524d9375befb5e80fa61aa39a19d06/depofiles/quiche.DepoFile>
  - <https://github.com/victorstewart>
  - <https://github.com/ngtcp2/ngtcp2>
  - <https://github.com/ngtcp2/ngtcp2/commits>
- **Sources the enricher read:**
  - <https://github.com/ngtcp2/ngtcp2>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/README.rst>
  - <https://github.com/ngtcp2/ngtcp2/releases>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/includes/ngtcp2/ngtcp2.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/doc/source/programmers-guide.rst>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_conn.c>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_ksl.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_objalloc.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_balloc.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_opl.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_map.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_map.c>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/lib/ngtcp2_rob.h>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/configure.ac>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/CMakeLists.txt>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/.github/workflows/build.yml>
  - <https://github.com/ngtcp2/ngtcp2/blob/main/SECURITY.md>
  - <https://github.com/ngtcp2/ngtcp2/security/advisories/GHSA-f523-465f-8c8f>
  - <https://github.com/ngtcp2/ngtcp2/security/advisories/GHSA-4gmv-gf46-r4g5>
  - <https://github.com/ngtcp2/ngtcp2/issues>
  - <https://github.com/ngtcp2/ngtcp2/issues?q=performance>
  - <https://github.com/ngtcp2/ngtcp2/issues/2318>
  - <https://github.com/ngtcp2/ngtcp2/issues/1029>
  - <https://github.com/victorstewart/quicperf>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.ngtcp2.h>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.quiche.h>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.cpp>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.benchmark.h>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.networking.h>
  - <https://github.com/curl/curl/blob/master/docs/HTTP3.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ngtcp2/ngtcp2`) · [data/wave5/enrich/raw/github_com_ngtcp2_ngtcp2.json](../../../data/wave5/enrich/raw/github_com_ngtcp2_ngtcp2.json) (enrichment confidence 0.75)

</details>
