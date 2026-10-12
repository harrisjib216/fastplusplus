# KCP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Two-file C reliable-UDP ARQ library. It spends extra bandwidth to get much lower tail latency than ENet or TCP under packet loss.

| | |
|---|---|
| **Beats** | ENet (libenet) reliable UDP; README also claims a gain over TCP |
| **Claimed result** | Wiki excerpt of a worst-network-lag moment (timestamp 10:51.21): asio_kcp 291 295 269 268 231 195 249 230 225 204 versus enet 1563 1520 1470 1482 1438 1454 1412 1637 1588 1540 (mean about 246 vs about 1,510 ms, roughly 6x lower, derived from page data). The wiki and bench_mark.md text says 'The lag is less than 1 second when network lag happen. 3 times better than enet when lag happen.' Over the full public logs of the concurrent 500-byte run (enet_bench_test/bench_mark_log/enet_500.log and kcp_500.log, about 16:18 to 16:30): ENet mean 285 ms, p99 3,911 ms, max 8,179 ms vs KCP mean 126 ms, p99 574 ms, max 1,013 ms, but median ENet 62 ms vs KCP 80 ms (derived from page data). README claim vs TCP (first-party, no data): 30%-40% lower average latency and three times lower maximum latency at the cost of 10%-20% more bandwidth. |
| **Workload** | Real-time PvP game traffic over the public internet via home WiFi: client sends a 500-byte (or 50-byte) packet every 50 ms, server echoes it; KCP (through the asio_kcp wrapper) and ENet run at the same time on the same computer and worst-case lag when the network degrades is logged. |
| **Metric** | latency |
| **Adoption** | 16.9k stars; README lists use in games and Alibaba Cloud, with ports in Go, Rust, Java and C# |
| **Last commit** | 2026-06-23 |
| **Links** | [repository](https://github.com/skywind3000/kcp) · [benchmark](https://github.com/skywind3000/kcp/wiki/KCP-Benchmark) |

## Verdict

The asio_kcp author, independent of KCP's author, ran an informal internet test: a home Wi-Fi/ADSL client sent a 500-byte message every 50 ms to an internet server, which echoed it. KCP (via asio_kcp, aggressive nodelay settings) and ENet 1.3.13 (default RTT lowered to 50 ms) ran at the same time from the same computer for about 12 minutes; no hardware, compiler or loss rate was recorded. In the full public logs KCP had mean 126 ms, p90 243, p99 574 and max 1,013, against ENet's 285, 657, 3,911 and 8,179, and ENet spent 7.2% of samples above 1 s vs KCP's 0.01%; ENet's median was lower (62 vs 80 ms) (all derived from page data). The README also embeds an Improbable SpatialOS chart (50 entities at 60 Hz): KCP's RTT stays near 30 ms through p99, vs about 105-190 ms for TCP and 32-110 ms for RakNet over p90-p99 (read off the chart). The test conditions are in a blog post that was not reachable here.

## Use it when

- Real-time multiplayer games, remote control or telemetry: small messages (tens to hundreds of bytes) every 10-50 ms over lossy Wi-Fi or mobile links, where p99 and worst-case delay matter more than bandwidth. The asio_kcp run logged p99 574 ms vs ENet's 3,911 ms.
- You already own a UDP socket or event loop, or another datagram path such as a relay, a P2P hole-punched socket or a tunnel, and want reliability without adopting a networking framework. It is two files and makes no system calls.
- Both ends are in different languages and need the same protocol: kcp-go/kcptun, C#, Java, Rust, Kotlin and other ports exist.
- Embedded or unusual platforms: plain C with no OS dependencies and a pluggable allocator (ikcp_allocator).

## Skip it when

- You need encryption, authentication, connection setup, multiplexed streams or standard interoperability. Use a QUIC stack (ngtcp2, picoquic, LSQUIC) instead. KCP packets are plaintext, and any datagram with the right 32-bit conv is accepted.
- Median latency on a decent link, or bulk throughput, is what matters. In the asio_kcp logs ENet had the lower median (62 vs 80 ms). The README puts KCP's bandwidth cost at 10-20%, and fast mode with nc=1 ignores congestion and is unfair to competing flows.
- Large messages: message mode refuses anything that needs 128 or more fragments, about 174 KB at the default 1400-byte MTU (ikcp_send returns -2; issues #428, #441).
- Many thousands of connections ticked by a naive loop: every ikcpcb needs ikcp_update calls, so schedule them with ikcp_check or a timer wheel.
- The default configuration (nodelay 0, 100 ms interval, 100 ms minimum RTO): the published latency wins all used aggressive nodelay settings.

## How it is fast

KCP recovers from loss with latency first in mind. It uses selective repeat: every header carries a cumulative UNA, plus a dedicated ACK per segment. Fast retransmit fires after `resend` later ACKs skip a segment. In nodelay mode the minimum RTO drops from 100 ms to 30 ms, and each timeout grows a segment's RTO by 1.5x (nodelay=1) or by rx_rto/2 (nodelay=2) instead of TCP's doubling. ACKs go out on every flush tick, with no delayed-ACK timer. nc=1 removes the congestion window so only the send and receive windows limit what is in flight. Segments have a 24-byte header and are packed several per MTU-sized datagram. KCP 2.x (May 2026) adds pluggable congestion control (struct IKCPOPS) with optional pacing.

## Compared with alternatives

The catalogued siblings are QUIC stacks (ngtcp2, picoquic, LSQUIC, quiche, TQUIC) and DNS servers. Pick KCP for a tiny, unencrypted reliability layer for small real-time messages on a UDP path you already control, when tail latency under loss is the goal. Pick a QUIC stack when you need TLS 1.3, connection management, streams, standard congestion control or interop.

## Integration

| | |
|---|---|
| **Form** | source-drop (ikcp.h + ikcp.c); a CMake static/shared library target and a vcpkg port also exist |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | Plain C that also builds as C++ (test.cpp #includes ikcp.c). The bundled CMakeLists.txt requires CMake 4.0+, so older CMake users should just compile the two files. |
| **Platforms** | any: no system calls; the caller supplies the datagram output function and a millisecond clock |
| **Thread safety** | None: drive each ikcpcb from one thread or put it behind an external lock. ikcp_allocator changes a process-wide allocator. |
| **Drop-in for the baseline** | false: ENet owns sockets, hosts, peers and channels, while KCP is only the ARQ layer, so you write the UDP loop and session management yourself or use a wrapper such as asio_kcp. |

## Gotchas

- The benchmark used more aggressive settings than the documented turbo mode (1, 10, 2, 1). asio_kcp's kcp_bench_mark_test tag calls ikcp_nodelay(kcp, 1, 2, 1, 1) on the client and (1, 5, 1, 1) on the server: a 2-5 ms internal clock and a retransmit after a single skipped ACK. ENet's default RTT was lowered from 500 to 50 ms. KCP's own simulator (test.cpp, 10% loss, 60-125 ms RTT) shows how much the mode matters: default mode averages 740 ms RTT (max 1,507) vs 138 ms (max 392) in fast mode. That simulator compares KCP modes only; the README's '30%-40% lower average latency than TCP' has no data in the repo.
- Master has been KCP 2.x since 2026-05-15 (tags v2.0.0 and v2.1.1; stable v1 moved to the v1 branch), and every published benchmark predates it. This corrects the record's 'protocol code is stable': the congestion-control and cwnd code changed in May 2026. Open issue #461 (2026-08-23), confirmed in current ikcp_flush: xmit, rto and resendts are updated before the pacing-budget check, so a segment skipped by pacing counts as sent. With a pacing congestion-control plugin this fakes losses and can trip dead_link; the built-in algorithm has no pacing and is unaffected. The Windows exports.def written by CMakeLists.txt also omits ikcp_setcc.
- Open issue #438: with the default IKCP_FASTACK_CONSERVE, ikcp_input updates maxack only when an ACK's ts is strictly newer (`_itimediff(ts, latest_ts) > 0`). Segments sent in one flush share a ts, so a batch of their ACKs keeps the lowest sn, and fast retransmit can fire less often than configured. The code is unchanged in current master.
- Nothing notifies you when a link dies. After dead_link (20) transmissions of one segment, kcp-&gt;state becomes -1 and the application has to poll it. Packets with a foreign conv return -1 from ikcp_input, so route datagrams with ikcp_getconv first. ikcp_wndsize silently raises the receive window to at least 128.

## Known shortcomings

- Informal one-off internet run by the asio_kcp author with no hardware or loss rate; the wiki excerpt is one bad moment. Full enet_bench_test logs: KCP has the better tail (p99 574 vs 3,911 ms) but ENet the better median (62 vs 80 ms); the wiki says '3 times better', not 'more than'. The TCP claim has no data.
- Enricher: asio_kcp ran ikcp_nodelay(1,2,1,1) on the client and (1,5,1,1) on the server, more aggressive than the README turbo mode; all benchmarks predate KCP 2.0 (2026-05-15), which reworked congestion control; open #461 (pacing bug in ikcp_flush, confirmed) and #438 (maxack bug still in code); the Windows exports.def omits ikcp_setcc. The SpatialOS KCP/TCP/RakNet chart could not be checked (improbable.io blocked).

## Caveats and trade-offs

Independent measurement (asio_kcp author, libinzhangyuan/reliable_udp_bench_mark bench_mark.md) but an informal one-off run on a real internet path from a home WiFi/ADSL client to an internet server: no compiler, flags, CPU model or loss rate, units are not printed (milliseconds, consistent with the 50 ms send interval), and the wiki numbers are a pasted 10-sample log excerpt from one bad-network moment whose timestamp does not appear in the public enet_bench_test logs. The full public logs show KCP wins on tail latency (p99 574 vs 3,911 ms, max 1,013 vs 8,179 ms) but ENet has the lower median (62 vs 80 ms), so the win is tail latency under loss, not typical latency. ENet's ENET_PEER_DEFAULT_ROUND_TRIP_TIME was changed from 500 to 50 for the test. The wiki's own wording is '3 times better than enet', not 'more than three times'. The TCP claim in the README is first-party percentages with no public data in the repo. Recent commits (2026-06-19 to 2026-06-23) are README edits; the protocol code is stable. Category dns-quic-http3 is a loose fit: KCP is a generic reliable-UDP ARQ, not QUIC or HTTP/3.

Spends 10%-20% extra bandwidth for lower latency; pure algorithm in two files (ikcp.h, ikcp.c) with no I/O, so the caller supplies UDP send and the clock and must call update every 10-20 ms; gives up TCP fairness in fast mode; documentation mainly in Chinese.

## Maintenance

Active: 16.9k stars, MIT, last commit 2026-06-23 (README edits), and two files that are trivial to vendor. Take the v1 branch for the long-proven code, because the May 2026 v2 congestion-control rework is unbenchmarked and has an open pacing bug (#461).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement by the asio_kcp author (not the KCP author) with public test code (libinzhangyuan/enet_bench_test, asio_kcp tag kcp_bench_mark_test) and public raw logs, run concurrently against ENet on the same machine and path; no compiler, flags, CPU or loss rate, and it is an informal one-off internet run rather than a reproducible lab setup, so B and not A.
- **Verifier notes:** Wiki and linked bench_mark.md confirm the KCP-vs-ENet comparison and the sample numbers; MIT, 16.9k stars and last commit 2026-06-23 confirmed. Shortcomings: informal single internet run, no hardware or loss rate, wiki excerpt is a cherry-picked bad moment; full logs show KCP wins tail latency (p99 574 vs 3,911 ms) but loses on median (80 vs 62 ms); TCP claim has no data.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** asio_kcp logs (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/skywind3000/kcp/wiki/KCP-Benchmark>
  - <https://github.com/skywind3000/kcp>
  - <https://github.com/skywind3000/kcp/commits/master.atom>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/README.md>
  - <https://raw.githubusercontent.com/libinzhangyuan/reliable_udp_bench_mark/HEAD/bench_mark.md>
  - <https://raw.githubusercontent.com/libinzhangyuan/enet_bench_test/HEAD/bench_mark_log/enet_500.log>
  - <https://raw.githubusercontent.com/libinzhangyuan/enet_bench_test/HEAD/bench_mark_log/kcp_500.log>
- **Sources the enricher read:**
  - <https://github.com/skywind3000/kcp>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/README.md>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/README.en.md>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/ikcp.h>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/ikcp.c>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/test.h>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/protocol.txt>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/skywind3000/kcp/HEAD/images/spatialos-50.png>
  - <https://github.com/skywind3000/kcp/wiki/KCP-Benchmark>
  - <https://github.com/skywind3000/kcp/commits/master.atom>
  - <https://github.com/skywind3000/kcp/commits/master.atom?after=20>
  - <https://github.com/skywind3000/kcp/tags.atom>
  - <https://github.com/skywind3000/kcp/commit/19459fa64dac0477621efa2b0f3dd1ff93fc2b38>
  - <https://github.com/skywind3000/kcp/issues>
  - <https://github.com/skywind3000/kcp/issues/461>
  - <https://github.com/skywind3000/kcp/issues/438>
  - <https://github.com/skywind3000/kcp/issues/454>
  - <https://raw.githubusercontent.com/libinzhangyuan/reliable_udp_bench_mark/HEAD/bench_mark.md>
  - <https://raw.githubusercontent.com/libinzhangyuan/enet_bench_test/HEAD/README.md>
  - <https://raw.githubusercontent.com/libinzhangyuan/enet_bench_test/HEAD/bench_mark_log/enet_500.log>
  - <https://raw.githubusercontent.com/libinzhangyuan/enet_bench_test/HEAD/bench_mark_log/kcp_500.log>
  - <https://github.com/libinzhangyuan/asio_kcp/tree/kcp_bench_mark_test>
  - <https://github.com/libinzhangyuan/asio_kcp/tags.atom>
  - <https://raw.githubusercontent.com/libinzhangyuan/asio_kcp/kcp_bench_mark_test/readme.md>
  - <https://raw.githubusercontent.com/libinzhangyuan/asio_kcp/kcp_bench_mark_test/client_with_asio/kcp_client.cpp>
  - <https://raw.githubusercontent.com/libinzhangyuan/asio_kcp/kcp_bench_mark_test/server_lib/connection.cpp>
  - <https://raw.githubusercontent.com/libinzhangyuan/asio_kcp/kcp_bench_mark_test/server_lib/connection.hpp>
  - https://improbable.io/blog/kcp-a-new-low-latency-secure-network-stack (EGRESS_BLOCKED)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/skywind3000/kcp`) · [data/wave5/enrich/raw/github_com_skywind3000_kcp.json](../../../data/wave5/enrich/raw/github_com_skywind3000_kcp.json) (enrichment confidence 0.75)

</details>
