# mTCP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> User-level, per-core TCP stack over DPDK/PSIO/netmap with an epoll-like API; beats Linux kernel sockets+epoll on short connections.

| | |
|---|---|
| **Beats** | epoll (Linux kernel TCP/IP stack) |
| **Claimed result** | Abstract: small-message transactions 25x faster than the latest Linux TCP stack and 3x faster than MegaPipe (best prior research system); popular applications 33% to 320% faster than on Linux. Sec 5.1: at 8 cores the 64B-message benchmark is 25x vs Linux 3.10.12 without SO_REUSEPORT, 5x vs Linux with SO_REUSEPORT, and 3x vs MegaPipe; connection accept is 13x/7.5x/5x vs Linux/REUSEPORT/multiprocess. lighttpd (SpecWeb2009 static files) is 3.2x/2.2x/1.5x vs Linux/REUSEPORT/MegaPipe; the SSLShader proxy is +18% to +33%. |
| **Workload** | Short-lived TCP connection handling / small-message request-response transactions on multicore Linux, plus ported applications (e.g. lighttpd) comparing the user-level mTCP stack to the stock Linux TCP stack. |
| **Metric** | throughput |
| **Hardware** | Server: 1x 8-core Intel Xeon E5-2690 @ 2.90 GHz, 32 GB RAM, Intel 82599 10 GbE NIC; mTCP on Linux 2.6.32 (PSIO), baseline Linux 3.10.12 (ixgbe-3.17.3), MegaPipe on Linux 3.1.3 |
| **Adoption** | 2.1k stars |
| **Last commit** | 2019-11-18 |
| **Links** | [repository](https://github.com/mtcp-stack/mtcp) · [benchmark](https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-jeong.pdf) |

## Verdict

NSDI'14 paper, one 8-core Xeon E5-2690 @ 2.90 GHz with an Intel 82599 10 GbE NIC, mTCP over PSIO on Linux 2.6.32, compiler not stated. In a 64 B one-message-per-connection server test at 8 cores, mTCP was 25x Linux 3.10.12 sockets+epoll with a shared listen socket, 5x Linux with SO_REUSEPORT and 3x MegaPipe; connection accept was 13x Linux, and lighttpd static-file serving was 3.2x/2.2x/1.5x Linux/REUSEPORT/MegaPipe.

## Use it when

- Research or reproduction work: studying kernel-bypass TCP, reproducing NSDI'14 numbers, or using a small C stack (about 11.5K LoC in the paper) as a baseline or a base to fork.
- Many concurrent short connections with small messages (roughly 64 B to a few KiB) on a multicore Linux box, where accept()/epoll_wait()/write() syscall cost and a shared accept queue are the bottleneck.
- HTTP load generation: epwget and the ported ab can saturate 10 GbE from fewer client machines (the paper cites more than a 4x cut in ab machines).
- An existing epoll-based, event-driven C/C++ server you can port mostly by renaming calls, running on a dedicated Intel NIC (82599/X710 class) with its own cores and a pinned kernel/DPDK 18.05 environment.

## Skip it when

- Production services. There have been no master commits since 2019-11; kernel-5.x builds break in igb_uio and dpdk-iface-kmod (#292, #310); and one user measured a 16 ms 4 KiB ping-pong on direct 10G and called it not production-ready (#306).
- Long-lived bulk transfers. In the paper, 8,000 connections each sending a 100 MiB file used 294% CPU versus 80% for Linux, because there is no TSO/LSO/LRO; socket buffers are also fixed-size (default 8 KiB) with no auto-tuning.
- Low-concurrency or latency-critical RPC. Batching raised min/median latency (9 vs 0 ms and 13 vs 3 ms at 8K connections) even though mean and max fell, and the maintainer says batching can hurt latency at low concurrency (#289).
- You need IPv6, UDP, real socket options, kernel services (netfilter/firewall, tc), or several processes sharing the NIC. mtcp_socket accepts only AF_INET/SOCK_STREAM, and the paper supports one application per NIC port.
- Cloud VMs or non-Intel NICs. The tested NIC list is Intel only; VMs need SR-IOV VFs and code tweaks (#267); DPDK busy-polls one core per mTCP thread at 100% unless built with ENFORCE_RX_IDLE.

## How it is fast

Each core runs one mTCP thread next to one application thread. NIC RSS (with a symmetric key) keeps each flow on one core, so the flow hash table, TCB and buffer pools, socket-id space and accept queue are all per-core, and the app and stack communicate over lock-free single-producer/single-consumer job and event queues. Packet I/O and flow events are batched (the paper averages \~2,170 events per scheduling period), so one app/stack context switch covers many connections, replacing per-call syscalls. It also queues control and ACK packets ahead of data packets, uses preallocated hugepage-backed memory pools and cache-line-split TCBs, and runs retransmission timers in millisecond hash buckets.

## Compared with alternatives

Pick mTCP over F-Stack only when you want a small, purpose-built short-connection stack to study, benchmark against, or fork. F-Stack ports the full FreeBSD 13 stack, ships Nginx/Redis integrations and an epoll/kqueue API, and was still getting commits in 2026-09, so it is the practical choice for production kernel bypass. IX's catalogued results use mTCP as a baseline, so mTCP is also the reference point when evaluating newer dataplanes.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | One packet-I/O backend: DPDK (git submodule pinned to v18.05, plus the bundled dpdk-iface-kmod module), PSIO (GPL-2.0 ps_ixgbe driver), netmap, or openNetVM. Also libnuma, libpthread, librt, libgmp (DPDK/ONVM), kernel headers, hugepages and a NIC bound to igb_uio. Optional libccp (Rust toolchain) for CCP congestion control. |
| **Minimum toolchain** | C built with GCC via autotools (-O3 -fgnu89-inline -Werror -m64); maintainer says clang was never really tested (#264). The DPDK path builds on kernels up to about 4.15 (fails on 5.3/5.9, #292/#310); PSIO needs Linux 2.6.32-2.6.38. |
| **Platforms** | Linux x86-64 only (tested on Xeon E5-2690 / Core i7-3770). NICs: Intel 82598/82599 (ixgbe), I350 (igb), X710/X722 (i40e); RSS queue count must be &gt;= MAX_CPUS (compile-time, default 16). |
| **Thread safety** | Per-thread by design: every call takes an mctx_t bound to one core's mTCP thread, and socket ids are local to that context, so a socket should only be used from its owning thread (cross-thread use asked in #303, unanswered). App-to-stack handoff uses lock-free SPSC queues. Open bug #329: static locals in RunMainLoop (core.c:787-788) are shared by all per-core mTCP threads, which is a data race on the RX path. |
| **Drop-in for the baseline** | partial — the calls map 1:1 to BSD sockets and epoll (mtcp_socket/accept/read/write, mtcp_epoll_create/ctl/wait), but every call needs an mctx_t, ids are not kernel fds, the app must be restructured into one event loop per core, and mtcp_epoll only watches mTCP sockets and mtcp_pipe()s |

## Gotchas

- mtcp_setsockopt() validates the socket id and returns 0 without doing anything, and mtcp_getsockopt() supports only SO_ERROR (api.c). TCP_NODELAY, SO_RCVBUF and similar options are silently ignored; buffer sizes come only from the config file (rcvbuf/sndbuf).
- RSS core affinity is required: the NIC must provide one RSS queue per mTCP core, and clients should call mtcp_init_rss() so their source ports hash back to the calling core. The remote peer must have TCP timestamps enabled (README).
- One user reports that mtcp_epoll_wait reports writability only once, as if edge-triggered, so mtcp_epoll_ctl had to be re-armed before every wait (#297, unresolved).
- The stack shares the app's address space, so app bugs can corrupt TCP state (the paper calls this fate-sharing). Removing the igb_uio/ps_ixgbe driver while running makes the app panic, and the bundled ab-mtcp counts mTCP init time in its results, which understates throughput on short runs (#289).

## Known shortcomings

- The headline 25x is against Linux 3.10.12 without SO_REUSEPORT; against Linux with SO_REUSEPORT it is 5x (3x vs MegaPipe). Needs DPDK/netmap-style NIC access (io_engine is GPL-2.0) and its own socket API, not a drop-in for epoll. Abandoned since 2019-11. No compiler or flags stated.
- mtcp_setsockopt silently ignores options (TCP_NODELAY, buffer sizes); open data race in RunMainLoop statics (#329). Worse than Linux on bulk transfers (no TSO/LRO) and higher median latency at 8K connections. IPv4/TCP only, DPDK pinned to v18.05, builds fail on Linux 5.x (#292, #310).

## Caveats and trade-offs

NSDI 2014 peer-reviewed paper; the CPU is stated but the compiler and flags are not, so the tier is B. The headline 25x is against Linux WITHOUT SO_REUSEPORT (a shared accept queue); against Linux with SO_REUSEPORT the gain is 5x at 8 cores. The baseline apps use the kernel's BSD sockets + epoll (the paper's Fig. 2 shows accept()/epoll_wait() vs mtcp_accept()/mtcp_epoll_wait()). The 2014 results used the PSIO driver on Linux 2.6.32. The core is BSD-3-Clause (GitHub reports NOASSERTION because of the template '&lt;organization&gt;' placeholder), but io_engine/ (PSIO driver) is GPL-2.0 and the dpdk submodule has its own licenses. There have been no commits on master since 2019-11.

Requires a dedicated packet-I/O driver (DPDK, PacketShader, or netmap) and cores reserved for the mTCP stack; exposes its own epoll-like API rather than drop-in POSIX sockets, so applications must be ported.

## Maintenance

Abandoned: master's last commit was 2019-11-18 and devel's 2020-01, with DPDK pinned at 18.05 and a 2024 'has development stopped?' issue left without a maintainer reply. The core is BSD-3-Clause and copyable, but io_engine is GPL-2.0 and reviving it on a modern kernel/DPDK means porting work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'14 paper compares mTCP against the stock Linux 3.10.12 TCP stack (BSD sockets + epoll, with and without SO_REUSEPORT) and MegaPipe; it names the CPU (Intel Xeon E5-2690 @ 2.90 GHz) and the benchmark apps are public in the repo (apps/example/epserver.c, epwget.c, apps/apache_benchmark, apps/lighttpd-1.4.32), but no compiler or flags are given, so it is not A.
- **Verifier notes:** Numbers are verified in the paper's abstract, intro and Sec 5; I clarified that the 25x is against the non-SO_REUSEPORT configuration. The license was confirmed from the LICENSE text (Modified BSD); 2138 stars, not archived, not a fork, last commit 2019-11-18.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-jeong.pdf>
  - <https://github.com/mtcp-stack/mtcp>
  - <https://github.com/mtcp-stack/mtcp/blob/master/LICENSE>
  - <https://github.com/mtcp-stack/mtcp/tree/master/apps/example>
  - <https://github.com/mtcp-stack/mtcp/blob/master/io_engine/COPYING>
- **Sources the enricher read:**
  - <https://github.com/mtcp-stack/mtcp>
  - <https://github.com/mtcp-stack/mtcp/blob/master/README.md>
  - <https://github.com/mtcp-stack/mtcp/blob/master/LICENSE>
  - <https://github.com/mtcp-stack/mtcp/blob/master/.gitmodules>
  - <https://github.com/mtcp-stack/mtcp/blob/master/README.config>
  - <https://github.com/mtcp-stack/mtcp/blob/master/README.devel>
  - <https://github.com/mtcp-stack/mtcp/blob/master/apps/example/README>
  - <https://github.com/mtcp-stack/mtcp/blob/master/config/sample_mtcp.conf>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/include/mtcp_api.h>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/include/mtcp_epoll.h>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/include/mtcp.h>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/api.c>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/core.c>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/dpdk_module.c>
  - <https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/Makefile.in>
  - <https://github.com/mtcp-stack/mtcp/branches>
  - <https://github.com/mtcp-stack/mtcp/commits/master>
  - <https://github.com/mtcp-stack/mtcp/commits/devel>
  - <https://github.com/mtcp-stack/mtcp/issues>
  - <https://github.com/mtcp-stack/mtcp/issues/337>
  - <https://github.com/mtcp-stack/mtcp/issues/306>
  - <https://github.com/mtcp-stack/mtcp/issues/297>
  - <https://github.com/mtcp-stack/mtcp/issues/303>
  - <https://github.com/mtcp-stack/mtcp/issues/329>
  - <https://github.com/mtcp-stack/mtcp/issues/292>
  - <https://github.com/mtcp-stack/mtcp/issues/310>
  - <https://github.com/mtcp-stack/mtcp/issues/269>
  - <https://github.com/mtcp-stack/mtcp/issues/267>
  - <https://github.com/mtcp-stack/mtcp/issues/289>
  - <https://github.com/mtcp-stack/mtcp/issues/264>
  - <https://github.com/DPDK/dpdk/commit/a5dce55556286cc56655320d975c67b0dbe08693>
  - <https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-jeong.pdf>
  - <https://github.com/F-Stack/f-stack>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/mtcp-stack/mtcp`) · [data/wave5/enrich/raw/github_com_mtcp_stack_mtcp.json](../../../data/wave5/enrich/raw/github_com_mtcp_stack_mtcp.json) (enrichment confidence 0.82)

</details>
