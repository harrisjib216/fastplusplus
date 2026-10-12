# quic-zig

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Pure-Zig QUIC/HTTP/3/WebTransport stack; \~3% faster than quiche on handshake rate in one harness, slower almost everywhere else.

| | |
|---|---|
| **Beats** | quiche |
| **Claimed result** | Connect only: 286 vs 277 conn/s p50 syscall (1.03x, derived from page data; pairwise quiche/quic-zig 0.968, CI 0.961-0.990) and 267 vs 258 conn/s io_uring (1.03x). In the same run quic-zig is slower than quiche in the other 21 of 23 publishable pairwise comparisons, all syscall unless noted: upload 10.642 vs 14.794 Gbps (0.72x), flow control 0.82x, multistream download 3.166 vs 10.990 Gbps (0.29x), request/response 3,704 vs 64,574 rps (\~17x slower), and \~13-20x slower on stream churn, small-payload messages, 0-RTT and close/reset. Resumed connect is 14.6 vs 305.9 conn/s (\~21x slower, io_uring). Idle footprint is \~3.7x larger (464,384 vs 125,440 bytes/connection, inconclusive row). |
| **Workload** | quicperf loopback harness: Connect scenario (full handshake plus bidirectional stream creation, count mode capped at 128 handshakes per sample), CUBIC, shared TLS 1.3 Ed25519 material, syscall backend. quic-zig ran with 8 client threads and quiche with 16; a saturation scout chose each library's thread count. Each row has 20 samples in 5 randomized blocks, and both rows are publishable. quic-zig runs as a Zig packet engine behind the harness's C++-owned UDP I/O. |
| **Metric** | other |
| **Compiler and flags** | quic-zig built from the fork victorstewart/quic-zig at commit 97a7bec (quicperf-tls-wall-clock, 2026-05-18) via depofiles/quiczig.DepoFile, with zig build -Doptimize=ReleaseFast -Dcpu=native; CMakeLists.txt hints Zig 0.16.0 x86_64-linux. The C++ harness is C++20 -O3 -march=native with LTO. quiche 0.29.0 was built with -C target-cpu=native -C opt-level=3 and fat LTO. The exact C++ compiler is not published. |
| **Adoption** | 57 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/endel/quic-zig) · [benchmark](https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md) |

## Verdict

quicperf (victorstewart/quicperf, loopback, CUBIC, CPU model not recorded) measured the quic-zig fork commit 97a7bec, built with Zig 0.16.0 ReleaseFast and -Dcpu=native, against quiche 0.29.0 built with fat LTO and target-cpu=native. On Connect, quic-zig reached 286 vs 277 conn/s p50 with the syscall backend (8 vs 16 client threads; pairwise ratio 0.968, CI 0.961-0.990) and 267 vs 258 conn/s with io_uring, but it lost to quiche in 21 of 23 pairwise comparisons, by up to \~21x.

## Use it when

- You are writing in Zig and want QUIC, HTTP/3 or WebTransport built into your program with no C or Rust toolchain in the build.
- You want a WebTransport or Media over QUIC server for browsers, with WebSocket fallback on the same port and event loop.
- The workload is dominated by connection setup (full 1-RTT handshakes), where quic-zig roughly matches quiche and other stacks.
- The traffic is mostly unreliable DATAGRAM frames: quicperf measured \~3.55M DATAGRAMs/s, second only to quiche's \~5.1M (quiche's rows are inconclusive).
- You are doing QUIC research or prototyping and prefer a readable, spec-annotated codebase over peak throughput.

## Skip it when

- Request/response, stream-churn, small-message, 0-RTT or close/reset workloads: in quicperf, quic-zig levels off at \~3,700-3,900 ops/s against quiche's 46k-75k, so quiche is 13-20x faster.
- Bulk transfer: quiche is 1.2-1.6x faster on upload and flow control and 3.5x faster on multistream download (3.17 vs 10.99 Gbps).
- Session resumption: quicperf measured 14-15 conn/s against quiche's \~306. Quinn, noq, s2n-quic and Neqo show the same 14-15 plateau, so the harness may be part of the cause.
- Many idle connections: quicperf measured \~464 KB per connection against quiche's \~125 KB (the row is inconclusive).
- Production or internet-facing use: the README says 'Not production-ready' and that the public APIs may change. Contributed security-fix PRs (#6-#12) have been open since March 2026.

## How it is fast

No documented technique explains the one win. On Connect, all 12 stacks fall between 234 and 306 conn/s, so the \~3% edge over quiche most likely reflects the harness, not quic-zig's design. The benchmarked May 2026 fork commit had none of upstream's later speed work. Upstream added that work in September 2026: a keyed AES-GCM context that sets up each key once, and a lower GHASH 8-way aggregation threshold (16 blocks instead of std's 84). Together these took encrypting a 1200 B packet on arm64 from 607 ns to 455 ns. Upstream also added sendmmsg plus UDP_SEGMENT (GSO) send batching to its own event loop, which quicperf bypasses because the harness owns the UDP I/O.

## Compared with alternatives

Pick quic-zig over ngtcp2, TQUIC or picoquic only when you need a pure-Zig stack with WebTransport and MoQ built in. For speed, ngtcp2 is \~1.5-2x quiche on bulk transfer and TQUIC is \~2.4x quiche on request rate in the same harness, while quic-zig trails quiche on both.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | libxev (pinned to the maintainer's fork, endel/libxev); no C libraries |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon) |
| **Platforms** | Linux, macOS, FreeBSD (src/sys.zig). Windows support is an open PR (#33). On x86-64, build with AES and PCLMUL CPU features (-Dcpu=native or x86_64_v3+aes+pclmul), or AES-GCM runs in software about 35x slower. |
| **Thread safety** | Not thread-safe per connection: sessions may only be used from the thread running the server's loop. To use several cores, run one server per thread, each on its own loop (reuse_port or the steering-worker router). |
| **Drop-in for the baseline** | no |

## Gotchas

- The low-level tls13.TlsConfig defaults skip_cert_verify to true, which skips chain and CertificateVerify checks. The high-level ClientConfig defaults it to false. PR #12 would change the low-level default and has been open since 2026-03-17.
- On Linux the event loop uses epoll by default, not io_uring, because io_uring setup fails in some containers. On macOS it uses kqueue. Config.max_connections defaults to 256.
- BENCHMARK.md shows 11,009 vs 1,114 req/s against quiche, but that quiche figure comes from quiche's example server with mio, which handles connections one after another, measured on macOS. quicperf finds quiche \~17x faster at request/response, so do not treat BENCHMARK.md as a like-for-like comparison.
- The quicperf numbers come from victorstewart/quic-zig 97a7bec, whose base commit upstream main is now 255 commits ahead of. That base predates the AES-GCM and GSO changes, so current upstream may benchmark differently.

## Known shortcomings

- Not faster than quiche: its only win is connect rate (\~3%, a scenario where all 12 libraries sit within 234-306/s), and quiche beats it in 21 of 23 comparisons, 13-21x on request, stream and resumption workloads. quicperf tested a fork commit, not upstream; the project claims nothing about performance.
- The repo's BENCHMARK.md (11,009 vs 1,114 req/s vs quiche) uses quiche's single-connection mio example on macOS, not a fair comparison. quicperf tested a May 2026 fork commit, 255 commits behind main. Low-level TlsConfig defaults skip_cert_verify to true (fix PR #12 open). Not production-ready; forked libxev; Zig 0.16.

## Caveats and trade-offs

quicperf (victorstewart/quicperf, 27 stars) is a small personal harness. It records no CPU model (machine_hash only), and the 2026-06-01 run came from a dirty working tree. It benchmarks a fork commit of quic-zig (victorstewart/quic-zig 97a7bec, which switches TLS certificate validity to wall clock), not upstream endel/quic-zig. The only win is \~3% on Connect, where all 12 stacks cluster at 234-306 conn/s. quic-zig is slower than quiche in 21 of 23 publishable pairwise comparisons, by up to \~21x. quic-zig's own README makes no performance claims.

quic-zig is a young Zig QUIC packet engine (the C++ harness owns UDP I/O); it loses to quiche by a wide margin on nearly every other quicperf scenario (download 10.463 vs 11.258 Gbps, upload 10.642 vs 14.794 Gbps, request/response 3,716 vs 64,574 qps), so this is a narrow, workload-specific win, not general superiority.

## Maintenance

Actively developed (last push 2026-09-25) and MIT-licensed, but self-described as not production-ready, rebuilt with AI assistance in 2026, and pinned to a forked libxev and Zig 0.16.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification B, tier now C.
- **Tier reason:** latest-results.md has the cited Connect rows (quic-zig syscall 286 vs quiche syscall 277 conn/s p50, both publishable), and pairwise-comparisons.tsv confirms the edge (quiche/quic-zig 0.968, CI 0.961-0.990). The harness code and flags are public, but no CPU model is recorded, and quicperf is a small personal harness (27 stars). That makes it tier C, not A or B, matching batch 22's ruling on this harness.
- **Verifier notes:** Rejected as not-faster. The row numbers are accurate, but the lone \~3% Connect edge (a harness-clustered metric) sits among 21 losses to quiche, 13-21x on request, stream and resumption workloads, and the project does not claim to be faster. quiche's Connect row used 16 client threads, not 8. If the entry is kept under the keep-and-document policy, use the corrected fields at tier C. Metadata checks out: MIT, 57 stars, last commit 2026-09-25, active, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/blob/main/CMakeLists.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/quiczig.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/quiche.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/pairwise-comparisons.tsv>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/publication-results.tsv>
  - <https://github.com/endel/quic-zig>
  - <https://github.com/victorstewart/quic-zig/commit/97a7becfcc09e6401c45e620c27eb09fb8a9b739>
- **Sources the enricher read:**
  - <https://github.com/endel/quic-zig>
  - <https://github.com/endel/quic-zig/blob/main/README.md>
  - <https://github.com/endel/quic-zig/blob/main/BENCHMARK.md>
  - <https://github.com/endel/quic-zig/blob/main/PRIORITIES.md>
  - <https://github.com/endel/quic-zig/blob/main/CHANGELOG.md>
  - <https://github.com/endel/quic-zig/blob/main/CLAUDE.md>
  - <https://github.com/endel/quic-zig/blob/main/build.zig.zon>
  - <https://github.com/endel/quic-zig/blob/main/DECISIONS/zig_std_divergences.md>
  - <https://github.com/endel/quic-zig/blob/main/src/sys.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/xev_backend.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/event_loop.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/c_api.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/quic/ecn_socket.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/quic/congestion.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/quic/tls13.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/quic/packet_packer.zig>
  - <https://github.com/endel/quic-zig/blob/main/src/quic/connection_manager.zig>
  - <https://github.com/endel/quic-zig/issues>
  - <https://github.com/endel/quic-zig/pulls>
  - <https://github.com/endel/quic-zig/pull/12>
  - <https://github.com/endel/quic-zig/compare/a80e10ea9f25221980e1107f126410c827b384c4...main>
  - <https://github.com/victorstewart/quic-zig/commit/97a7becfcc09e6401c45e620c27eb09fb8a9b739>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/pairwise-comparisons.tsv>
  - <https://github.com/victorstewart/quicperf/blob/main/zig-packet-ffi/src/lib.zig>
  - <https://github.com/victorstewart/quicperf/blob/main/zig-packet-ffi/include/quicperf_zig_packet_ffi.h>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/endel/quic-zig`) · [data/wave5/enrich/raw/github_com_endel_quic_zig.json](../../../data/wave5/enrich/raw/github_com_endel_quic_zig.json) (enrichment confidence 0.4)

</details>
