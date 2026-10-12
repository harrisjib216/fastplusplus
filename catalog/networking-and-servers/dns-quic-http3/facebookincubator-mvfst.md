# mvfst

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Meta's C++ IETF QUIC transport (client+server) under Proxygen HTTP/3; cut Facebook-app tail latency 20% vs HTTP/2-over-TCP.

| | |
|---|---|
| **Beats** | HTTP/2 over TCP (Facebook's prior production transport stack) |
| **Claimed result** | vs HTTP/2: 6% fewer request errors, 20% lower tail latency, 5% smaller response headers on dynamic requests; on video: mean time between rebuffering improved up to 22%, video error count down 8%, rate of video stalls down 20%. |
| **Workload** | Production staged rollout of QUIC/HTTP-3 (built on mvfst + Proxygen) across the Facebook and Instagram apps for dynamic API requests and video delivery, at global scale, eventually covering more than 75% of Facebook's internet traffic. |
| **Metric** | latency |
| **Adoption** | 1.66k stars; powers QUIC/HTTP-3 for the Facebook and Instagram apps |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/facebook/mvfst) · [benchmark](https://engineering.fb.com/2020/10/21/networking-traffic/how-facebook-is-bringing-quic-to-billions/) |

## Verdict

Meta's staged production rollout of QUIC/HTTP-3 (mvfst + Proxygen, BBR as primary congestion control) in the Facebook app, against its prior HTTP/2-over-TCP stack, reported 20% lower tail latency (percentile unstated), 6% fewer request errors and 5% smaller response headers on dynamic requests, plus up to 22% better mean time between rebuffering, 8% fewer errors and 20% fewer stalls on video. No hardware, compiler, network mix or fixed workload is given, and app flow-control and bandwidth heuristics were retuned, so this measures the protocol switch, not mvfst's code speed.

## Use it when

- HTTP/3 or custom QUIC for mobile apps (Android/iOS) on lossy or high-latency networks where tail latency, request errors and video rebuffering matter more than bulk throughput.
- You already run Folly/Fizz/Proxygen, or will adopt them, and want the QUIC stack that serves Meta's own app traffic.
- Large server fleets behind an L4 load balancer: connection-ID routing that works with Katran, per-worker CPU scaling, and APIs for zero-downtime socket takeover during restarts.
- Congestion-control work: Cubic, NewReno, Copa, BBR, BBR2 and static-cwnd/none ship in-tree, a Custom controller type can be plugged in, and Meta's MVFST-RL reinforcement-learning congestion-control framework targets it.
- Linux servers that can use GSO/sendmmsg batching, MSG_ZEROCOPY or the optional io_uring backend to lower per-packet syscall cost.

## Skip it when

- Maximum bulk throughput per core: in the 'QUIC on the Highway' 10G benchmark (early-2023 builds), an mvfst client+server pair reached 1198 Mbit/s vs 2506 for quiche and 3004 for LSQUIC (TCP/TLS: 8010). In 2020 the maintainers cited &gt;3 Gbps single stream on one thread and 4-5 Gbps at best on 10G, limited by kernel copies and crypto.
- CPU-constrained servers: a maintainer stated (2020) that HTTP/3 over mvfst is 'not less performant than TCP + HTTP/2, albeit at a higher per-transaction CPU cost'.
- Small footprint, embedded use or a C ABI: it pulls in Folly, Fizz, Boost, fmt, glog, gflags and OpenSSL, has no C API, and builds are heavy (users report getdeps filling /tmp).
- Old platforms: the build includes linux/if_xdp.h, so the maintainers require Linux 4.18+ (CentOS 7 fails), and GCC 7 toolchains fail on the dependencies.
- You need a stable API or semver: the README calls the API alpha, and releases are weekly date-tagged snapshots (e.g. v2026.09.21.00) that must match folly/fizz snapshots.

## How it is fast

The measured gains are protocol-level: QUIC over UDP multiplexes streams without TCP's cross-stream head-of-line blocking, and Meta ran it with BBR as its primary congestion controller, retuning app flow-control limits and bandwidth-estimation heuristics that had been implicitly tuned for TCP. On the implementation side, the server uses a thread-local worker per core with connection IDs that encode host, worker and process IDs, so an L4 load balancer (Katran) and in-process routing avoid cross-thread handoff and survive zero-downtime restarts. Meta cut CPU cost with UDP GSO batching (also sendmmsg and sendmmsg+GSO writers), smoother userspace packet pacing, and reworked data structures for unacknowledged packets. Recent code adds an optional io_uring event-base backend, MSG_ZEROCOPY sends and an AF_XDP sender.

## Compared with alternatives

Pick mvfst over LSQUIC, ngtcp2, picoquic, TQUIC or quiche when you are on Meta's Folly/Fizz/Proxygen stack or need its fleet features (Katran-aware connection-ID routing, socket takeover, pluggable BBR/Copa); pick LSQUIC or ngtcp2 when goodput per core or a small C library matters. Like Google QUICHE's entry, its evidence is a production A/B against the operator's own TCP stack, not a cross-stack benchmark.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake builds per-module static libraries, or one monolithic shared libmvfst when building shared; shared builds have had macOS link failures) |
| **Dependencies** | folly, fizz (TLS 1.3), Boost &gt;=1.69 (headers), fmt, glog, gflags, OpenSSL, Threads; optional liburing (io_uring backend) and libev (alternative event base). Built most easily with Meta's getdeps.py, which fetches and builds matching versions. |
| **Minimum toolchain** | C++20 (top-level CMakeLists sets CMAKE_CXX_STANDARD 20), CMake 3.14+; minimum compiler versions not documented (GCC 7 fails). |
| **Platforms** | Linux (4.18+ per maintainers; GSO, io_uring and AF_XDP are Linux-only), macOS and Windows (CI builds via getdeps), plus Android/iOS mobile build variants; architecture requirements not documented. |
| **Thread safety** | Event-loop bound: each QuicSocket belongs to one QuicEventBase, and the headers require calls such as attach/detachEventBase from that event base's thread. The server scales with one QuicServerWorker per event-base thread, and stats callbacks are created per worker without cross-thread synchronization. There is no general thread-safety statement. |
| **Drop-in for the baseline** | false: it replaces TCP as the transport, so both client and server must adopt it, and HTTP semantics need Proxygen's HTTP/3 layer on top. |

## Gotchas

- Defaults are not the tuned production setup: TransportSettings default to Cubic, pacingEnabled=false and batchingMode=NONE (no GSO). Maintainers say tperf defaults 'are not great' and need GSO, a large cwnd, large flow-control windows and more streams to reach Gbps rates.
- The conservative default UDP send size (kDefaultV4UDPSendPacketLen = 1252 bytes) and small default flow-control windows (65 KiB per stream, 1 MiB per connection) cap throughput on high-bandwidth-delay links. One user got \~290 Mbit/s on a 500 Mbit/s emulated link until raising the receive window (#166).
- Security history: CVE-2021-24029 (a crafted packet causes a crash via a failed assertion, CVSS 7.5) and CVE-2025-30403 (heap-buffer-overflow, CVSS 8.1, fixed in v2025.07.07.00). Until a 2026 fix, replayed packets were decrypted and processed again (#428). Track the weekly tags.
- Performance depends on the peer: in the 10G study the mvfst-client/picoquic-server pair got only 52 Mbit/s, and over emulated GEO satellite links mvfst did well as a server but poorly as a client.

## Known shortcomings

- Evidence is Meta's 2020 production rollout (20% lower tail latency, 6% fewer errors, 5% smaller headers, up to 22% less video rebuffering vs HTTP/2 over TCP): wins for QUIC as a protocol, not a measure of mvfst's own code speed; the post says mvfst's CPU efficiency had to be optimized. No fixed workload or hardware. Repo moved to github.com/facebook/mvfst.
- The 2020 production A/B also retuned BBR, app flow control and bandwidth heuristics; no hardware, compiler, workload or tail percentile given; 5% smaller headers has no stated cause. Maintainers say HTTP/3 over mvfst has higher per-transaction CPU cost than TCP+HTTP/2 (#124) and tops out around &gt;3 Gbps per stream per thread, 4-5 Gbps on 10G (#127). Over emulated GEO satellite links it does well as a server, poorly as a client (arXiv 2202.08228). Defaults aren't the production config: Cubic, pacing off, no GSO, 1252-byte UDP payload, 65 KiB per-stream and 1 MiB per-connection windows (#166). CVE-2021-24029 (assertion crash, CVSS 7.5), CVE-2025-30403 (heap overflow, CVSS 8.1, fixed v2025.07.07.00); replayed packets were re-processed until a 2026 fix (#428). README calls the API alpha; weekly date-tagged snapshots with no semver/ABI promise; heavy dependencies (folly, fizz, Boost, fmt, glog, gflags, OpenSSL); Linux 4.18+, CentOS 7/GCC 7 fail, macOS shared builds broken (#326); now C++20.

## Caveats and trade-offs

First-party production A/B numbers with no fixed workload, hardware, or compiler/flags stated, so tier is capped at C. These are protocol-level wins (QUIC+HTTP/3 with BBR vs TCP+HTTP/2, after retuning app heuristics and flow control), not a measurement of mvfst's code speed. The post itself says mvfst's CPU efficiency was a concern that had to be optimized (GSO, pacing, unacked-data structures), and no comparison against another QUIC stack is made. The baseline is 'HTTP/2 over TCP', not one of the category's named baselines (msquic/quiche/nghttp3), so baseline_in_list=false. The repo has moved to github.com/facebook/mvfst (the facebookincubator URL redirects).

C++14/17, tightly coupled to Facebook's Proxygen and Folly; the reported gains come from a live production A/B rollout, not a controlled lab benchmark, so they mix client population and network-condition effects with pure protocol-implementation speed.

## Maintenance

Actively developed by Meta (last push 2026-09-26, weekly date-tagged snapshots up to v2026.09.21.00) and MIT-licensed, but the README still calls the API alpha, and in practice it builds only with matching Folly/Fizz versions via getdeps.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Meta engineering post (2020-10-21) reporting production A/B results for QUIC/HTTP-3 vs HTTP/2 over TCP. It gives no fixed workload, benchmark code, hardware or compiler details, so tier C.
- **Verifier notes:** All numbers match the page: 6% fewer request errors, 20% lower tail latency, 5% smaller response headers vs HTTP/2; video MTBR up to 22% better, 8% fewer video errors, 20% fewer stalls; &gt;75% of traffic on QUIC. Metadata checks out: MIT, 1662 stars, last commit 2026-09-26, not archived, not a fork. The GitHub API resolves the repo to facebook/mvfst, so the orchestrator may want to update repo_url.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** 'QUIC on the Highway' 10G study (arXiv 2309.16395, early-2023 builds): an mvfst client+server pair reached 1198 Mbit/s vs quiche 2506, LSQUIC 3004 and TCP/TLS 8010 Mbit/s; mvfst client to picoquic server only 52 Mbit/s.
- **Pages the verifier opened:**
  - <https://engineering.fb.com/2020/10/21/networking-traffic/how-facebook-is-bringing-quic-to-billions/>
  - <https://github.com/facebookincubator/mvfst>
- **Sources the enricher read:**
  - <https://github.com/facebook/mvfst>
  - <https://github.com/facebook/mvfst/blob/main/README.md>
  - <https://github.com/facebook/mvfst/blob/main/CMakeLists.txt>
  - <https://github.com/facebook/mvfst/blob/main/quic/CMakeLists.txt>
  - <https://github.com/facebook/mvfst/blob/main/cmake/MvfstFunctions.cmake>
  - <https://raw.githubusercontent.com/facebook/mvfst/main/build/fbcode_builder/CMake/FBBuildOptions.cmake>
  - <https://github.com/facebook/mvfst/blob/main/quic/server/QuicServer.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/server/QuicServerBackendIoUring.cpp>
  - <https://github.com/facebook/mvfst/blob/main/quic/api/QuicSocket.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/api/QuicSocketLite.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/api/QuicGsoBatchWriters.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/state/TransportSettings.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/state/StateData.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/state/OutstandingPacket.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/QuicConstants.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/codec/DefaultConnectionIdAlgo.h>
  - <https://github.com/facebook/mvfst/blob/main/quic/xsk/BaseXskContainer.h>
  - <https://github.com/facebook/mvfst/tags>
  - <https://github.com/facebook/mvfst/issues/124>
  - <https://github.com/facebook/mvfst/issues/127>
  - <https://github.com/facebook/mvfst/issues/166>
  - <https://github.com/facebook/mvfst/issues/221>
  - <https://github.com/facebook/mvfst/issues/223>
  - <https://github.com/facebook/mvfst/issues/233>
  - <https://github.com/facebook/mvfst/issues/339>
  - <https://github.com/facebook/mvfst/issues/364>
  - <https://github.com/facebook/mvfst/issues/428>
  - <https://engineering.fb.com/2020/10/21/networking-traffic/how-facebook-is-bringing-quic-to-billions/>
  - <https://arxiv.org/abs/2309.16395>
  - <https://arxiv.org/abs/2202.08228>
  - <https://arxiv.org/abs/2201.02577>
  - <https://arxiv.org/abs/1910.04054>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=mvfst>
  - <https://hn.algolia.com/api/v1/search?query=mvfst>
  - https://interop.seemann.io/latest/result.json (404, not used)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/facebookincubator/mvfst`) · [data/wave5/enrich/raw/github_com_facebookincubator_mvfst.json](../../../data/wave5/enrich/raw/github_com_facebookincubator_mvfst.json) (enrichment confidence 0.8)

</details>
