# gnet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Pure-Go epoll/kqueue multi-reactor TCP/UDP framework; 1.4-1.95x Go net's packet rate on streaming 1KB echo.

| | |
|---|---|
| **Beats** | Go standard library net package (runtime netpoller over epoll) |
| **Claimed result** | Echo benchmark, 1KB packet, Linux: gnet had the highest QPS (tcpkali packet-rate estimate) at every connection count vs. Go std net: 1000 conns 4,646,164 vs 3,250,189 (\~1.43x); 2000 conns 4,374,275 vs 2,371,727 (\~1.84x); 5000 conns 3,191,612 vs 2,285,845 (\~1.40x); 10000 conns 2,619,695 vs 1,343,247 (\~1.95x) (ratios derived from page data) |
| **Workload** | TCP echo-server benchmark with 1KB packets over tcpkali, at 1000/2000/5000/10000 concurrent connections on Linux, comparing gnet against Go's standard `net` package (its runtime netpoller wraps epoll on Linux), tidwall/evio, and CloudWeGo netpoll. |
| **Metric** | throughput |
| **Hardware** | 8 CPU cores, AMD EPYC 7K62 48-Core Processor, 16GB RAM, Ubuntu 20.04/x86_64 |
| **Compiler and flags** | go1.17.2 linux/amd64; go build -gcflags="-l=4" -ldflags="-s -w" for all servers, plus -tags=poll_opt for gnet (bench-echo.sh); GOMAXPROCS=8; gnet v1.5.3 per go.mod at the chart commit |
| **Adoption** | 11,251 stars; the README's use-case list names Tencent, Tencent Games, iQIYI, Xiaomi, 360, Baidu Tieba, JD, Zuoyebang and ByteDance as production users |
| **Last commit** | 2026-07-03 |
| **Links** | [repository](https://github.com/panjf2000/gnet) · [benchmark](https://github.com/gnet-io/gnet-benchmarks) |

## Verdict

The Oct 2021 chart in gnet-benchmarks (gnet v1.5.3 built with -tags=poll_opt, Go 1.17.2, GOMAXPROCS=8, 8 cores of an AMD EPYC 7K62, client and server on localhost) shows tcpkali streaming 1KB echo packet-rate estimates of 1.40-1.95x Go net across 1k-10k connections; later raw logs at 1000 connections (Dec 2021, and Jan 2022 labelled gnet v2) show about 1.36-1.41x more bytes echoed. A closed-loop Fortio ping-pong run in the same repo (Feb 2022, 1000 conns, 1KB) shows only 446k vs 389k QPS (1.15x), with better median but worse p99 latency.

## Use it when

- Go services holding thousands to 10k+ long-lived TCP connections with small messages (game servers, push/IM gateways, custom RPC or Redis-protocol servers) where per-connection goroutines and scheduler overhead dominate.
- You own the wire protocol and are willing to write framing/codec code on top of Next/Peek/Discard.
- Linux production using epoll (optionally built with -tags=poll_opt,gc_opt), or macOS kqueue.
- Throughput per core matters more than tail latency, and handlers are short and non-blocking (blocking work goes to pkg/pool/goroutine, replies via AsyncWrite).
- UDP servers that want SO_REUSEPORT fan-out across several event loops.

## Skip it when

- You need TLS, HTTP, WebSocket or gRPC out of the box: none is built in (TLS and io_uring are unchecked roadmap items), and the README says gnet's TechEmpower HTTP code is benchmark-only and not production-ready.
- Existing net.Conn code or libraries (crypto/tls, net/http, bufio-based parsers) that you do not want to rewrite into callbacks; deadlines are unsupported.
- Latency-sensitive request/response at moderate connection counts: the benchmark repo's own Fortio ping-pong run (1000 conns, 1KB) gives gnet only 1.15x Go net's QPS with a worse p99 (15.8 ms vs 10.2 ms).
- Proxies or gateways relaying large streams to slow clients: there is no read backpressure, so outbound buffers grow until OOM (issue #722, closed as not planned).
- Windows production: the README says the Windows build is for development and testing only.

## How it is fast

Multi-reactor design: N event-loop goroutines (one per CPU with WithMulticore, optionally pinned with WithLockOSThread) each own an epoll/kqueue fd and call epoll_wait/read/write directly via golang.org/x/sys/unix, bypassing the Go runtime netpoller and per-connection goroutines; with SO_REUSEPORT each loop gets its own listener, otherwise a main reactor accepts and load-balances (round-robin, least-connections, source-addr hash). Each loop reads into one shared buffer and passes OnTraffic a slice of it, so only unconsumed bytes are copied into a per-connection elastic ring buffer, and Write goes straight to the socket, spilling to an outbound buffer only on EAGAIN. After events the loop re-polls with a 0 ms timeout plus runtime.Gosched before blocking, and the poll_opt build tag (used in the benchmark) stores the connection's attachment pointer in epoll_event.data to skip the fd-to-conn map lookup.

## Compared with alternatives

Every catalogued sibling (libhv, PhotonLibOS, Seastar, monoio, uWebSockets, Asio io_uring, etc.) is C, C++ or Rust; pick gnet when the service must stay in Go and you want an epoll/kqueue reactor instead of goroutine-per-connection. If you can leave Go or want io_uring, which gnet lacks, the C/C++/Rust siblings are the comparison set.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | panjf2000/ants/v2 (goroutine pool), valyala/bytebufferpool, go.uber.org/zap, gopkg.in/natefinch/lumberjack.v2, golang.org/x/sys, golang.org/x/sync |
| **Minimum toolchain** | Go 1.20 (go.mod; CI tests Go 1.20 and 1.26) |
| **Platforms** | Linux (epoll; syscall defs for amd64, 386, arm, arm64, ppc64/ppc64le, riscv64, s390x, mips) and macOS (kqueue) tested in CI; FreeBSD/NetBSD/OpenBSD/DragonFly only cross-compiled in CI; Windows for dev/test only |
| **Thread safety** | Each connection belongs to one event-loop goroutine. Reader methods, Write/Writev/Flush, Context/SetContext and LocalAddr/RemoteAddr are not concurrency-safe and must be called inside EventHandler callbacks; AsyncWrite/AsyncWritev, Wake, Close/CloseWithCallback, Socket setters and SafeContext/SetSafeContext (v2.10.0+) are safe from any goroutine. |
| **Drop-in for the baseline** | no |

## Gotchas

- Slices returned by Next/Peek point into the event loop's shared read buffer; copy them before passing to another goroutine or using them after Discard.
- Calling Write or Context from your own goroutine produces 'fatal error: concurrent map read and map write' crashes (issues #741, #720, #632, #577); use AsyncWrite or SafeContext instead.
- Anything that blocks in OnTraffic, OnOpen or an AsyncCallback (which runs on the loop) stalls every connection on that event loop.
- Do not touch a Conn after OnClose: before a fix, fd reuse could send writes to a new connection (#621); open issue #765 reports Enroll blocking forever during shutdown and leaked dup'd fds on failed Enroll.

## Known shortcomings

- Only 1 of 8 chart numbers appears in any raw log, and the metric is tcpkali packet rate (streaming, no replies), not request QPS; the same repo's closed-loop ping-pong run shows \~1.15x QPS with worse p99 (15.8 vs 10.2 ms). Results not re-run since 2022-02. No backpressure (outbound buffers grow to OOM, #722); Conn methods are not concurrency-safe. Go, not C++.

## Caveats and trade-offs

Numbers come from a chart committed Oct 2021 (backed by raw tcpkali logs in results/echo_linux.txt) in gnet-io/gnet-benchmarks (39 stars, last commit Dec 2024). It measured gnet v1.5.3 on Go 1.17.2, not current gnet v2 or newer Go netpollers. Both gnet and Go net use epoll underneath, so the real baseline is Go's std net, not epoll itself. The QPS values are tcpkali packet-rate estimates over localhost with 8 cores. A companion TechEmpower Round 22 plaintext claim (gnet ranked #1 of 486) is chart-only in the README, and the README admits gnet's TechEmpower HTTP code is benchmark-tuned and not production-ready.

Event-driven callback model instead of Go's one-goroutine-per-connection blocking style, so migrating existing `net`-based code requires a rewrite; narrower feature surface than `net` (core TCP/UDP/Unix-socket only); author states gnet's TechEmpower HTTP entry is 'half-baked and fine-tuned for benchmark purposes only', not production-ready.

## Maintenance

Actively maintained (v2.10.0 released 2026-07-03, 2 open issues/PRs) and Apache-2.0, usable as an ordinary Go module, but the published benchmarks date from 2021-2022 and have not been rerun on current gnet or Go.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code in gnet-io/gnet-benchmarks (bench-echo.sh driving tcpkali against echo-gnet-server/main.go and echo-net-server/main.go), with compiler (go1.17.2 linux/amd64), build flags in bench-echo.sh (go build -gcflags="-l=4" -ldflags="-s -w", plus -tags=poll_opt for gnet) and CPU (8 cores of AMD EPYC 7K62) all stated. The chart values are backed by raw tcpkali logs in results/echo_linux.txt.
- **Verifier notes:** Chart numbers match the record exactly. The record's claim that gnet powers ByteDance's Kitex and Hertz is false: both depend on cloudwego/netpoll according to their go.mod files. ByteDance is only listed as a gnet user in the README. Baseline was changed from epoll to Go std net because gnet itself is epoll-based.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/panjf2000/gnet>
  - <https://github.com/panjf2000/gnet_benchmarks/raw/master/results/echo_conn_linux.png>
  - <https://github.com/gnet-io/gnet-benchmarks>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/bench-echo.sh>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/results/echo_linux.txt>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/results/echo_linux_1k_conn.txt>
  - <https://github.com/cloudwego/kitex>
  - <https://github.com/cloudwego/hertz>
- **Sources the enricher read:**
  - <https://github.com/panjf2000/gnet>
  - <https://github.com/panjf2000/gnet/blob/dev/go.mod>
  - <https://github.com/panjf2000/gnet/blob/dev/gnet.go>
  - <https://github.com/panjf2000/gnet/blob/dev/options.go>
  - <https://github.com/panjf2000/gnet/blob/dev/engine_unix.go>
  - <https://github.com/panjf2000/gnet/blob/dev/eventloop_unix.go>
  - <https://github.com/panjf2000/gnet/blob/dev/connection_unix.go>
  - <https://github.com/panjf2000/gnet/blob/dev/reactor_default.go>
  - <https://github.com/panjf2000/gnet/blob/dev/reactor_ultimate.go>
  - <https://github.com/panjf2000/gnet/blob/dev/load_balancer.go>
  - <https://github.com/panjf2000/gnet/blob/dev/conn_matrix.go>
  - <https://github.com/panjf2000/gnet/blob/dev/conn_map.go>
  - <https://github.com/panjf2000/gnet/blob/dev/pkg/netpoll/poller_epoll_default.go>
  - <https://github.com/panjf2000/gnet/blob/dev/pkg/netpoll/poller_epoll_ultimate.go>
  - <https://github.com/panjf2000/gnet/blob/dev/pkg/pool/goroutine/goroutine.go>
  - <https://github.com/panjf2000/gnet/blob/dev/.github/workflows/test.yml>
  - <https://github.com/panjf2000/gnet/blob/dev/.github/workflows/cross-compile-bsd.yml>
  - <https://github.com/panjf2000/gnet/releases/tag/v2.10.0>
  - <https://github.com/panjf2000/gnet/issues?q=label%3Abug>
  - <https://github.com/panjf2000/gnet/issues/733>
  - <https://github.com/panjf2000/gnet/issues/722>
  - <https://github.com/panjf2000/gnet/issues/741>
  - <https://github.com/panjf2000/gnet/issues/662>
  - <https://github.com/panjf2000/gnet/issues/765>
  - <https://github.com/panjf2000/gnet/issues/621>
  - <https://github.com/panjf2000/gnet/issues/608>
  - <https://github.com/gnet-io/gnet-benchmarks>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/bench-echo.sh>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/echo-gnet-server/main.go>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/echo-net-server/main.go>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/go.mod>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/results/echo_linux.txt>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/results/echo_linux_1k_conn.txt>
  - <https://github.com/gnet-io/gnet-benchmarks/blob/master/results/echo_conn_1k_conn_v2.txt>
  - <https://gnet.host/docs/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/panjf2000/gnet`) · [data/wave5/enrich/raw/github_com_panjf2000_gnet.json](../../../data/wave5/enrich/raw/github_com_panjf2000_gnet.json) (enrichment confidence 0.8)

</details>
