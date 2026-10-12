# picoquic

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Minimal C QUIC/HTTP3 research stack; beats quiche by \~6-7% on bulk upload and connection setup in one loopback harness.

| | |
|---|---|
| **Beats** | quiche |
| **Claimed result** | \~1.06-1.07x quiche on bulk upload and connection setup (p50, derived from page data): upload syscall 15.823 vs 14.794 Gbps (1.07x; pairwise 95% CI 1.061-1.076), upload io_uring 14.549 vs 13.755 Gbps (1.06x), connect syscall 297 vs 277 conn/s (1.07x; CI 1.049-1.095). In the same run picoquic is slower than quiche in the other 18 of 21 publishable pairwise comparisons, all syscall: request/response 59,098 vs 64,574 rps (0.92x), flow control 0.94x, loss recovery 7.590 vs 11.689 Gbps (0.65x), small-payload messages 0.67x, close/reset 0.66x, 0-RTT 0.86x, multistream download 0.546 vs 10.990 Gbps (0.05x) and multistream upload 0.591 vs 15.291 Gbps (0.04x). Its bidirectional (0.22 vs 12.66 Gbps) and DATAGRAM rows are inconclusive. |
| **Workload** | quicperf loopback harness: Linux, C++-owned UDP I/O shared by all stacks, CUBIC, shared TLS 1.3 Ed25519 material, one pinned server thread. Upload is client-to-server bulk transfer (8-byte request plus bulk body, duration mode) on the syscall backend. picoquic ran with 2 client threads and quiche with 4; a saturation scout chose each library's thread count. Each row has 20 samples in 5 randomized blocks, and both rows are publishable. Also Connect (full handshake plus bidi stream creation, at most 128 handshakes per sample), syscall, 16 client threads each. |
| **Metric** | throughput |
| **Compiler and flags** | quicperf C++ harness: CMake Release, C++20, -O3 -march=native, LTO (CMakeLists.txt, README); exact compiler/version not published. picoquic pinned at master commit 2b1e14d (2026-05-16) with picotls 7c32032 (fusion on) and OpenSSL 4.0.0 via depofiles/picoquic.DepoFile. quiche 0.29.0 (e85fc8e) built with RUSTFLAGS='-C target-cpu=native -C opt-level=3', fat LTO, codegen-units=1. |
| **Adoption** | 776 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/private-octopus/picoquic) · [benchmark](https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md) |

## Verdict

The run is victorstewart/quicperf's 2026-06-01 loopback matrix: Linux, harness-owned UDP I/O, CUBIC, one pinned server thread, C++20 -O3 -march=native with LTO. The CPU model was not recorded and the harness tree was dirty. picoquic master 2b1e14d (picotls with fusion, OpenSSL 4.0.0) reached p50 upload of 15.82 vs 14.79 Gbps against quiche 0.29.0 (target-cpu=native, fat LTO) on syscall (1.07x, CI 1.061-1.076; picoquic had 2 client threads, quiche 4), 14.55 vs 13.76 Gbps on io_uring (1.06x), and 297 vs 277 handshakes/s (1.07x). It lost the other 18 of 21 publishable pairwise comparisons.

## Use it when

- One or two long bulk streams per connection, especially client-to-server upload: 15.8 vs 14.8 Gbps (syscall) and 14.5 vs 13.8 Gbps (io_uring) over quiche on loopback.
- Handshake-heavy loads where a small edge matters: 297 vs 277 full handshakes/s on syscall (the io_uring row was inconclusive).
- Transport research or experimentation: multipath draft, ACK frequency, BDP and timestamp extensions, and pluggable congestion control (cubic, bbr, bbr1, c4, prague, newreno, fastcc). Virtual time lets you test deterministically on a simulator.
- Embedding a small MIT-licensed C QUIC engine into your own event loop, io_uring or DPDK path, since the library never touches sockets or the clock itself.
- Non-HTTP protocols over QUIC (for example DNS over QUIC via the companion quicdoq project) or WebTransport and HTTP datagrams via h3zero.

## Skip it when

- Many concurrent streams on one connection: multistream download was 0.55-0.67 Gbps and multistream upload 0.59 Gbps, against quiche's 11-15 Gbps (16-26x slower) in the same run.
- RPC-style or lossy workloads: quiche beat it on request/response (0.92x syscall, 0.61x io_uring), small messages (0.67x), close/reset (0.66x), 0-RTT (0.86x) and loss recovery (7.6 vs 11.7 Gbps, 0.65x). Issues #1830 (Cubic stabilization after HyStart) and #1694 (HyStart vs Linux) are still open.
- High-rate unreliable DATAGRAM traffic: 72k-91k datagrams/s vs quiche's \~5.1-5.2M. Both rows were inconclusive, but the gap is 57-71x.
- Memory-constrained hosts carrying high-BDP flows: the docs warn of hundreds of MB per connection at gigabit rates unless you cap it, and idle footprint was 135 KB vs quiche's 125 KB per connection (syscall).
- Production multipath: it tracks an evolving draft, and 2026 fixes for multipath and qlog crashes (NULL derefs #2215 and #2136, qlog double-free #2152, #2188) show that code is still settling.

## How it is fast

The docs describe copy avoidance on both paths. Senders can use a just-in-time API: `picoquic_mark_active_stream` plus the `prepare_to_send` callback, where the app writes straight into the packet being formatted via `picoquic_provide_stream_data_buffer`, so there is no per-stream queue copy. Acknowledged packet structures are recycled through a per-context free list. On receive, a decrypted packet is queued to the stream as-is (no second copy) when the stream frame is its last frame. `picoquic_prepare_next_packet_ex` can return a train of packets for a single UDP GSO `sendmsg`. The benchmarked build used picotls's x86-64 'fusion' AES-GCM engine (loaded only if `ptls_fusion_is_supported_by_cpu()`), and picoquic grows flow-control credit automatically by default because 'flow control tends to limit performance'.

## Compared with alternatives

In the same quicperf run, ngtcp2 roughly doubles picoquic's bulk numbers (upload 31.0 vs 15.8 Gbps, download 18.2 vs 8.9-9.7 Gbps) and TQUIC leads on request rate (155k vs 59k rps), so choose those for raw throughput or RPC. Choose picoquic for its research extensions (multipath, BDP/timestamps, many congestion controllers, simulator) in a small MIT-licensed C codebase, or reach for its picoquic-DPDK fork if you can adopt kernel bypass.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target picoquic-core, plus optional picoquic-log and picohttp-core; shared libraries via BUILD_SHARED_LIBS since 2026-09-24) |
| **Dependencies** | picotls (required; -DPICOQUIC_FETCH_PTLS=Y fetches it) and OpenSSL 1.1.1/3.0 by default (the benchmark used 4.0.0). WITH_OPENSSL=OFF falls back to picotls minicrypto, whose AES-GCM the docs call 'very slow'. Threads required. Optional: MbedTLS, libaegis, liburing (WITH_IO_URING). |
| **Minimum toolchain** | C11 with extensions, CMake 3.13+; Visual Studio 2017 solution on Windows |
| **Platforms** | Linux, Windows, macOS, FreeBSD. CI runs on x86-64 VMs only; ARM32 and Apple M1 rely on user reports. The fusion AES-GCM engine is x86-64 only. |
| **Thread safety** | Not thread-safe. Use one QUIC context (with its connections) per thread and call the API only from that context's network thread, handing work over with picoquic_wake_up_network_thread. A WITH_THREAD_CHECK=ON debug build traps violations. |
| **Drop-in for the baseline** | no |

## Gotchas

- Since commit 8b8c302 (2026-09-17), CMake defaults PTLS_WITH_FUSION=OFF because unimplemented fusion stubs in the vendored picotls crash real connections. The benchmarked build (2b1e14d, May 2026) had fusion on, so a current-master build encrypts through OpenSSL, and nobody has measured whether the upload margin survives that.
- Cap memory up front with picoquic_set_cwin_max and picoquic_set_max_data_control. Flow-control credit already granted cannot be withdrawn, and out-of-order data holds whole received packets, so usage can exceed the flow-control limit when frames are small.
- A custom loop must call picoquic_prepare_next_packet_ex often enough. In #2190 the maintainer traced stop-and-go throughput to ACK gaps growing to hundreds of ms (keep them under \~25 ms), and the socket-loop docs warn against long work inside callbacks.
- Multithreaded servers keep resumption tickets and tokens per thread, and the ticket key is a per-process random value unless set in config. Resume/0-RTT across processes or hosts therefore needs a shared key, and clients only resume from the same thread.

## Known shortcomings

- Wins only 3 of 21 quicperf comparisons against quiche, each by 6-7%, and is 16-26x slower on multistream transfers. quicperf is a small personal harness with no CPU model, and its author also commits to picoquic.
- The benchmarked build used picotls fusion; since 2026-09-17 (commit 8b8c302) master defaults PTLS_WITH_FUSION OFF because fusion stubs crash connections, and no one has re-measured the \~6-7% upload margin with OpenSSL encryption. In the same quicperf run picoquic lost 18 of 21 comparisons to quiche, including multistream (16-26x slower), datagrams (57-71x, inconclusive rows) and idle memory (135 vs 125 KB per connection). 2026 crash fixes in multipath and qlog code (#2215, #2136, #2152, #2188). First GitHub release only on 2026-09-25.

## Caveats and trade-offs

quicperf (victorstewart/quicperf, 27 stars) is a small personal harness, not a well-known suite. Its author has 57 commits in private-octopus/picoquic, so the harness is not fully independent for this pair. docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt records only an anonymized machine_hash (no CPU model). The 2026-06-01 run came from a dirty working tree, with uncommitted edits to perf.picoquic.h, perf.quiche.h and other adapters on commit 3eda036. Loopback only. The wins are narrow: \~6-7% on upload (both backends) and on syscall connect, and connect rates for all 12 stacks cluster at 234-306 conn/s. picoquic loses to quiche in 18 of 21 publishable pairwise comparisons, by 16-26x on multistream transfers.

picoquic is a minimal, largely single-threaded reference/research QUIC stack. It only leads quiche on 2 of 16 quicperf scenarios (Upload throughput, Connect rate); quiche wins the other 14, often by a wide margin (e.g. request/response 64,574 vs 59,098 qps, stream churn 74,756 vs 48,480 streams/s), so this is workload-specific, not general superiority.

## Maintenance

Actively maintained under MIT: last push 2026-09-25, first GitHub release v2026.09.24.61fcd56, version string 1.1.53.0. It builds as a normal CMake library, but application docs are thin; the README points to picoquicdemo and the sample folder as the best starting points.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** latest-results.md has picoquic and quiche rows with the cited p50s (upload syscall 15.823 vs 14.794 Gbps; connect syscall 297 vs 277 conn/s; all four rows publishable), and pairwise-comparisons.tsv confirms them (upload 1.070 [CI 1.061-1.076], connect 1.071 [1.049-1.095]). The harness code (perf.picoquic.h, perf.quiche.h, depofiles/) and flags are public, but no CPU model is recorded. quicperf is also a small personal harness (27 stars) whose author contributes to picoquic, so it is neither A nor B; this is the same C ruling batch 22 gave ngtcp2 and TQUIC on this harness.
- **Verifier notes:** The numbers and row ownership check out (both cited rows publishable), but quiche's Upload row used 4 client threads, not 2; corrected in workload. Downgraded B to C to match batch 22's quicperf ruling (obscure harness, no CPU model). claimed_speedup now discloses that picoquic is slower than quiche on most quicperf scenarios. Metadata checks out: MIT, 776 stars, last commit 2026-09-25, active, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/blob/main/CMakeLists.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/picoquic.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/picotls.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/quiche.DepoFile>
  - <https://github.com/victorstewart/quicperf/tree/main/docs/results/fixed-full-matrix-max16-20260601T175816Z>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/pairwise-comparisons.tsv>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/publication-results.tsv>
  - <https://github.com/private-octopus/picoquic>
  - <https://github.com/private-octopus/picoquic/commit/2b1e14d5a46532eadf691edef5bd747da6de6557>
- **Sources the enricher read:**
  - <https://github.com/private-octopus/picoquic>
  - <https://github.com/private-octopus/picoquic/blob/master/README.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/architecture.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/parallel.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/memory.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/managing-memory-copies.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/socket_loop.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/send_receive_data.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/building_picoquic.md>
  - <https://github.com/private-octopus/picoquic/blob/master/doc/without_openssl.md>
  - <https://github.com/private-octopus/picoquic/blob/master/picoquic/picoquic.h>
  - <https://github.com/private-octopus/picoquic/blob/master/picoquic/picoquic_ptls_fusion.c>
  - <https://github.com/private-octopus/picoquic/blob/master/picoquic/sockloop.c>
  - <https://github.com/private-octopus/picoquic/blob/master/CMakeLists.txt>
  - <https://github.com/private-octopus/picoquic/blob/2b1e14d5a46532eadf691edef5bd747da6de6557/CMakeLists.txt>
  - <https://github.com/private-octopus/picoquic/blob/2b1e14d5a46532eadf691edef5bd747da6de6557/cmake/FindPTLS.cmake>
  - <https://github.com/private-octopus/picoquic/commits/master/CMakeLists.txt>
  - <https://github.com/private-octopus/picoquic/commit/8b8c302>
  - <https://github.com/private-octopus/picoquic/issues>
  - <https://github.com/private-octopus/picoquic/issues/2190>
  - <https://github.com/private-octopus/picoquic/issues/1615>
  - <https://github.com/private-octopus/picoquic/releases>
  - <https://github.com/victorstewart/quicperf>
  - <https://github.com/victorstewart/quicperf/blob/main/README.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/latest-results.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/methodology.md>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/pairwise-comparisons.tsv>
  - <https://github.com/victorstewart/quicperf/blob/main/docs/results/fixed-full-matrix-max16-20260601T175816Z/fixed-environment.txt>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.picoquic.h>
  - <https://github.com/victorstewart/quicperf/blob/main/perf.picoquic_seed.c>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/picoquic.DepoFile>
  - <https://github.com/victorstewart/quicperf/blob/main/depofiles/picotls.DepoFile>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/private-octopus/picoquic`) · [data/wave5/enrich/raw/github_com_private_octopus_picoquic.json](../../../data/wave5/enrich/raw/github_com_private_octopus_picoquic.json) (enrichment confidence 0.72)

</details>
