# Homa (HomaModule) — Linux kernel implementation of the Homa RPC transport protocol

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause OR GPL-2.0+ (per-file SPDX headers on the module and benchmark sources; a few test/tool files are BSD-1-Clause or GPL-2.0; no top-level LICENSE file)` · 🟢 active

> Linux kernel module for Homa, a message-based datacenter RPC transport with far lower short-message tail latency than TCP.

| | |
|---|---|
| **Beats** | TCP (and DCTCP) |
| **Claimed result** | 40-node cluster benchmark at high load (workloads W2-W5): for short messages, P99 latency is 19-72x lower than TCP and 7-83x lower than DCTCP (the abstract summarises this as 7-83x lower than TCP and DCTCP). For short messages, P50 is 3.5-7.5x lower than TCP and 2.7-3.8x lower than DCTCP. Homa's P50 and P99 are lower than TCP/DCTCP at every message size, but the 7-83x range applies only to short messages. Best-case 100-byte RTT: 15.1us (Homa) vs 23.4us (TCP) vs 24.1us (DCTCP). Client and server RPC rate: 1.6 vs 1.0 Mops/sec (60% higher). |
| **Workload** | 40-node CloudLab cluster; basic back-to-back single-client RPC latency/throughput (Table 2) plus four of the 'Montazeri' request/response workloads under high network load, measuring P50/P99/P999 tail latency across message sizes; Homa is explicitly designed as a transport for datacenter RPC frameworks (paper names gRPC and Apache Thrift as the frameworks it targets) |
| **Metric** | latency |
| **Hardware** | CloudLab xl170 nodes: Intel Xeon E5-2640v4 (10 cores, 2.4GHz), 4x16GB DDR4-2400, Intel DC S3520 480GB SSD, Mellanox ConnectX-4 25Gbps NIC, Mellanox 2410 switch, 40-node cluster |
| **Compiler and flags** | Not stated in the paper. The kernel module is built with kbuild against Linux 5.4.80 using the kernel's own flags. The repo's current util/Makefile builds the cp_node benchmark driver with g++ -Wall -Werror -fno-strict-aliasing -O3. No compiler version is given anywhere. |
| **Adoption** | 435 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/PlatformLab/HomaModule) · [benchmark](https://www.usenix.org/system/files/atc21-ousterhout.pdf) |

## Verdict

The USENIX ATC'21 paper compared this module (2021 code, Linux 5.4.80, MTU 3000) with Linux kernel TCP (TCP_NODELAY, per issue #51 and cp_node.cc) and DCTCP (ECN threshold 70 KB) on 40 CloudLab xl170 nodes (Xeon E5-2640v4, ConnectX-4 25 Gbps, one Mellanox 2410 switch). Under high load on workloads W2-W5, short-message P99 was 19-72x lower than TCP and 7-83x lower than DCTCP, and P50 was 3.5-7.5x and 2.7-3.8x lower. Best-case 100-byte RTT was 15.1 vs 23.4/24.1 us, and RPC rate was 1.6 vs 1.0 Mops/s. No compiler version or flags are stated. The author's unreviewed perf.txt log (Jan 2026, current code, 100 Gbps c6620, W4 at 80 Gbps) still shows short-message P99 of about 91-99 us for Homa versus 833-1272 us for TCP.

## Use it when

- Datacenter request/response traffic where P99 latency of short messages (hundreds of bytes to a few KB) under 50-80% network load is what hurts, e.g. fan-out services and storage/cache RPC.
- Mixed workloads with both short and long messages (the Montazeri W3-W5 shapes), where TCP's per-stream head-of-line blocking and switch queue buildup inflate tail latency.
- Highly connected clusters: one Homa socket reaches every peer, and the paper puts per-peer state at about 200 bytes versus about 2000 bytes per open TCP socket.
- You control the whole stack: Linux 6.17.8 (main) or RHEL 8/9.5 (branches) hosts, Mellanox ConnectX-4/5/6 or Intel E810 NICs, and top-of-rack switches you can configure for DSCP strict-priority queues.
- Transport research or benchmarking: the repo ships the cp_node/cp_vs_tcp/cp_bench harness, timetrace tools and /proc/net/homa_metrics used to produce its published numbers.

## Skip it when

- Bulk or single-stream throughput. In the paper's Table 2, one client doing 500 KB RPCs gets 10.0 Gbps versus 20.3 Gbps for TCP. Messages are capped at HOMA_MAX_MESSAGE_LENGTH = 1,000,000 bytes, so large transfers must be chunked.
- WAN or cross-datacenter links. The homa(7) man page says Homa is for RTTs of a few tens of microseconds and is not suitable for wide-area use.
- Anywhere you cannot load an out-of-tree kernel module or configure switches: managed cloud VMs, unprivileged containers, macOS and Windows. Upstream Linux does not include it (no net/homa in mainline as of v7.3-rc4).
- CPU-bound small-RPC servers. In the paper, 1.6 Mops/s used about 18 of 20 hyperthreads (\~0.1 M req/s/core, versus \~10 M for kernel-bypass eRPC), and perf.txt (Sep 2025) says receive polling costs an extra 2-3 cores.
- Hosts carrying heavy TCP traffic at the same time, or needing encryption. perf.txt (Jan 2026) shows Homa's short-message P99 rising about 4x when it shares hosts with TCP, and still about 30% worse with homa_qdisc. There is no TLS layer (grpc_homa supports only insecure channels).

## How it is fast

Receiver-driven flow control: a sender sends the first rtt_bytes of a message without asking, then sends more only when the receiver grants it. Receivers approximate SRPT (shortest remaining processing time first) with a bounded degree of overcommitment. Priorities are set through 8 switch priority queues keyed on DSCP bits, and a homa_prio daemon sets unscheduled-priority cutoffs from observed message sizes. A sender-side pacer/homa_qdisc keeps NIC queues short so small messages never wait behind large ones, and message framing removes TCP's head-of-line blocking. On the host side the ATC'21 paper credits most of the 100-byte RTT gain to busy-polling in recvmsg (\~4 us) and SoftIRQ core selection (3-4 us), and higher RPC rate to GRO batching across RPCs.

## Compared with alternatives

Pick HomaModule when tail latency of short RPCs under heavy network load is the problem and you can change host kernels and switch config. brpc, Kitex and rpcx win on QPS in user space but still run over TCP, so they keep its head-of-line blocking and congestion tails. grpc_homa is only a gRPC shim on top of this module, and its README says it has been unmaintained since late 2023 (gRPC 1.57, insecure channels only). Use it only if you must keep gRPC's API.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Kernel build tree/headers that match the running kernel (main: Linux 6.17.8; rhel8 and rhel9.5 branches; older linux_x.y branches are stale), a kernel built with IPv6 (Kconfig depends on IPV6), and root for insmod. The homa_prio user-space daemon (util/) is recommended. Full performance also needs switch priority queues, jumbo frames, and NIC TSO for Homa packets (Mellanox) or TCP hijacking. The optional C++ homa::receiver helper and homa.h UAPI header ship in the repo. |
| **Minimum toolchain** | Module is built with kbuild and the kernel's own compiler/flags (no GCC version documented). util/ tools and homa_receiver.cc need g++ with -std=c++17. |
| **Platforms** | Linux only. Tested on x86-64 (Intel xl170/c6620 and AMD c6525 CloudLab nodes per perf.txt); other architectures not documented. Verified NICs: Mellanox ConnectX-4/5/6 and Intel E810. |
| **Thread safety** | Multiple threads may use one socket: the man page describes several threads blocked on a socket, and cp_node runs several receiver/server threads per socket. The C++ homa::receiver helper is explicitly not thread-safe per instance. Processes can share a socket only if they map its receive-buffer region at the same virtual address. |
| **Drop-in for the baseline** | no |

## Gotchas

- Out of the box, performance is poor until the host and network are tuned. That means jumbo frames, NIC interrupt coalescing off, RPS on and RFS off, homa_qdisc configured on each tx queue, switch DSCP priority mapping, and TSO. INSTALL.md says software GSO is 'temporarily broken', so on NICs that won't segment Homa packets the fallback is TCP hijacking. Hijacked packets masquerade as TCP and can be dropped by datacenter switch filters.
- The API has changed repeatedly. Homa 2.0 (Dec 2022) moved to sendmsg/recvmsg with an app-supplied mmap'd buffer pool. homa_send/homa_recv/homa_reply were removed in May 2025, private-RPC flags changed in Mar 2025, and since Feb 2025 unbound sockets reject incoming requests. Netdev review is expected to change the API again.
- Receive buffers are registered up front (page-aligned region, 'tens of MB'). recvmsg returns ENOMEM when the pool is exhausted, and bpages are only returned to Homa on the next recvmsg. Raising the 1 MB message cap means editing a static_assert and recompiling every app (issue #48).
- The upstream series (v20, posted 2026-09-14) is stripped to about 8,000 of 20,000 lines, and its cover letter says its performance is 'about the same as TCP'. The fast paths (grant scheduling, qdisc, hijack, GRO offload) exist only in this out-of-tree repo. notes.txt also records grant 'stranding' under very high load in large clusters, capping throughput at about 60-70% of link bandwidth. One rtt_bytes value is used for all peers, and the SIGCOMM incast optimization is not implemented.

## Known shortcomings

- A transport protocol, not a gRPC/Thrift library: compared against Linux TCP and DCTCP. The 7-83x P99 gains apply to short messages only (P50 3.5-7.5x). Paper numbers are from 2021 code on Linux 5.4.80; the module has since been heavily reworked for kernel upstreaming. Needs a kernel module and Homa-capable peers. No compiler or flags stated.
- The fast version exists only out of tree: the upstream netdev series (v20, 2026-09-14) is stripped to \~8k lines and its cover letter says performance is about the same as TCP; mainline has no net/homa. Needs jumbo frames, interrupt coalescing off, RPS on, RFS off, homa_qdisc on every tx queue, DSCP priority queues and TSO; software GSO is 'temporarily broken' and the TCP-hijacking fallback can be dropped by switch filters. Bulk throughput loses (10.0 vs 20.3 Gbps single-client 500 KB); messages capped at 1 MB. CPU cost high (\~0.1 M req/s/core in the paper; polling costs 2-3 extra cores). Sharing hosts with TCP raises short-message P99 \~4x without homa_qdisc, \~30% with it. No encryption. Author notes grants get stranded at very high load (\~60-70% of link bandwidth). The homa_send/recv/reply API in the record was removed in 2025 (now sendmsg/recvmsg with SO_HOMA_RCVBUF). No compiler/flags; latest data is the repo's perf.txt (2026-01: P99 \~91-99 us vs 833-1272 us for TCP).

## Caveats and trade-offs

The 7-83x win is for P99 latency of short messages under high load, not for raw bandwidth. The paper's own Table 2 shows single-connection 500KB throughput where Homa (10.0 Gbps) is LOWER than TCP (20.3 Gbps); multi-RPC throughput is equal (23.8 vs 23.9 Gbps). The baseline is Linux kernel TCP/DCTCP, not gRPC or Thrift themselves; the RPC-framework link goes through the separate, less mature PlatformLab/grpc_homa shim (reported as a companion entry). The paper's numbers come from the 2021 code on Linux 5.4.80. The module has since been heavily reworked (Homa 2.0, sendmsg/recvmsg API, Linux 6.17.8, upstreaming under way since Oct 2024), so current performance may differ. The license exists only in per-file SPDX headers (no LICENSE file).

Requires a custom Linux kernel module (no macOS/Windows, no unprivileged/userspace-only path); new homa_send/homa_recv/homa_reply socket API is not backward-compatible with existing TCP/UDP socket code, so gRPC/Thrift apps need a shim (see grpc_homa) to use it transparently; needs specific NIC support (Mellanox ConnectX-4/5/6, Intel E810 verified); paper states small-message throughput is still 5-10x below raw NIC line rate due to software/kernel overhead.

## Maintenance

Actively maintained by John Ousterhout (last commit 2026-09-25, upstreaming in progress on netdev). BSD-2-Clause OR GPL-2.0+ via per-file SPDX headers, so it is copyable, but it is an out-of-tree kernel module that must be rebuilt and ported for each kernel version it runs on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed USENIX ATC 2021 paper compares Homa/Linux directly against Linux kernel TCP and DCTCP. The hardware is fully stated (Table 1: CloudLab xl170, Xeon E5-2640v4, ConnectX-4 25 Gbps, Linux 5.4.80), and the benchmark code is public (util/cp_node.cc driven by util/cp_bench, which the README says produced Figs 3-4). The compiler and flags are never stated for the kernel module or the kernel, so this falls short of A.
- **Verifier notes:** The paper's text is 'P99 19-72x lower than TCP and 7-83x lower than DCTCP' for short messages. The record's 'across all message sizes' overstated the 7-83x range, so claimed_speedup was corrected. The GitHub API reports license null, but a scan of 106 code files found SPDX 'BSD-2-Clause OR GPL-2.0+' on 93 of them. The rest are BSD-1-Clause, GPL, xxhash BSD-2 or a dual-licensed Wireshark dissector, plus one scratch.c/avg.py with no header, so usability is copyable. Metadata checked: 435 stars, not archived, not a fork, last commit 2026-09-25.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/atc21-ousterhout.pdf>
  - <https://github.com/PlatformLab/HomaModule>
  - <https://github.com/PlatformLab/HomaModule/blob/main/README.md>
  - <https://github.com/PlatformLab/HomaModule/blob/main/util/Makefile>
  - <https://github.com/PlatformLab/HomaModule/blob/main/Makefile>
  - <https://github.com/PlatformLab/HomaModule/blob/main/homa_plumbing.c>
  - <https://github.com/PlatformLab/HomaModule/blob/main/util/cp_node.cc>
  - <https://github.com/PlatformLab/HomaModule/blob/main/perf.txt>
- **Sources the enricher read:**
  - <https://github.com/PlatformLab/HomaModule>
  - <https://github.com/PlatformLab/HomaModule/blob/main/README.md>
  - <https://github.com/PlatformLab/HomaModule/blob/main/INSTALL.md>
  - <https://github.com/PlatformLab/HomaModule/blob/main/protocol.md>
  - <https://github.com/PlatformLab/HomaModule/blob/main/man/homa.7>
  - <https://github.com/PlatformLab/HomaModule/blob/main/man/sendmsg.2>
  - <https://github.com/PlatformLab/HomaModule/blob/main/man/recvmsg.2>
  - <https://github.com/PlatformLab/HomaModule/blob/main/homa.h>
  - <https://github.com/PlatformLab/HomaModule/blob/main/homa_receiver.h>
  - <https://github.com/PlatformLab/HomaModule/blob/main/Kconfig>
  - <https://github.com/PlatformLab/HomaModule/blob/main/Makefile>
  - <https://github.com/PlatformLab/HomaModule/blob/main/perf.txt>
  - <https://github.com/PlatformLab/HomaModule/blob/main/notes.txt>
  - <https://github.com/PlatformLab/HomaModule/blob/main/util/cp_node.cc>
  - <https://github.com/PlatformLab/HomaModule/blob/main/util/Makefile>
  - <https://github.com/PlatformLab/HomaModule/issues?q=is%3Aissue>
  - <https://github.com/PlatformLab/HomaModule/issues/5>
  - <https://github.com/PlatformLab/HomaModule/issues/9>
  - <https://github.com/PlatformLab/HomaModule/issues/48>
  - <https://github.com/PlatformLab/HomaModule/issues/51>
  - <https://github.com/PlatformLab/HomaModule/issues/53>
  - <https://github.com/PlatformLab/HomaModule/issues/85>
  - <https://github.com/PlatformLab/HomaModule/issues/105>
  - <https://github.com/PlatformLab/HomaModule/pulls?q=is%3Apr>
  - <https://www.usenix.org/system/files/atc21-ousterhout.pdf>
  - <https://github.com/PlatformLab/grpc_homa>
  - <https://github.com/torvalds/linux/tree/master/net/homa>
  - <https://lore.kernel.org/netdev/?q=s:homa>
  - <https://lore.kernel.org/netdev/20260914230517.1190-1-ouster@cs.stanford.edu/>
  - <https://hn.algolia.com/api/v1/search?query=Homa%20transport&tags=story>
  - <https://export.arxiv.org/api/query?search_query=abs:Homa>
  - <https://arxiv.org/abs/2312.15403>
  - <https://arxiv.org/abs/2406.15686>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/platformlab/homamodule`) · [data/wave5/enrich/raw/github_com_platformlab_homamodule.json](../../../data/wave5/enrich/raw/github_com_platformlab_homamodule.json) (enrichment confidence 0.86)

</details>
