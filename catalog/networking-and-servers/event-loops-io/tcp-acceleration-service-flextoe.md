# FlexTOE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Netronome Agilio SmartNIC TCP offload engine running the established-connection data path on-NIC; beats Linux, TAS and Chelsio TOE.

| | |
|---|---|
| **Beats** | Linux host TCP stack, TAS (TCP Acceleration as an OS Service), and the Chelsio Terminator hardware TCP offload engine |
| **Claimed result** | From the abstract, arXiv 2110.10919 and NSDI'22 alike: Memcached scales up to 38% better than TAS and saves up to 81% of host CPU cycles vs Chelsio. 99.99th-percentile RPC RTT is 3.2x lower than Chelsio and 50% lower than TAS. Single-connection RPC throughput is up to 2.4x TAS on x86 and 4x TAS on BlueField. The full paper's Linux-kernel-TCP figures: Memcached throughput up to 5.5x Linux, 4.9x Chelsio and 1.6x TAS (Fig. 8). RPC throughput at 250 cycles/RPC is up to 4x Linux and 5.3x Chelsio when receiving, and over 7.6x Linux and Chelsio when sending (Fig. 10). With up to 2K connections it reaches 3.3x Linux. FlexTOE loses in some cases: median small-RPC latency is 20 us vs 14 us for Chelsio and 16 us for TAS, and TAS is 1.5x better in the connection-scalability benchmark. |
| **Workload** | Memcached and RPC microbenchmarks on an Agilio-CX40 SmartNIC, plus single-connection RPC throughput on x86 and BlueField hosts |
| **Metric** | throughput |
| **Hardware** | Two 20-core Intel Xeon Gold 6138 @ 2 GHz servers (40 GB RAM), each with a Netronome Agilio CX40 40 Gbps, a Chelsio Terminator T62100-LP-CR 100 Gbps and an Intel XL710 40 Gbps NIC. Extra clients: two 2x18-core Xeon Gold 6154 @ 3 GHz (ConnectX-5 100 Gbps) and two 4-core Xeon E3-1230 v5 @ 3.4 GHz (82599ES 10 Gbps), on a 100 Gbps switch. The generalization runs used a Mellanox BlueField MBF1M332A-ASCAT 25 Gbps SmartNIC and a 32-core AMD EPYC 7452 @ 2.35 GHz host with a ConnectX-5 100 Gbps NIC. |
| **Compiler and flags** | SmartNIC firmware was built with the NFP compiler toolchain 6.1.0.1. The host compiler and flags are not stated. |
| **Adoption** | 62 stars; NSDI'22 paper |
| **Last commit** | 2022-02-27 |
| **Links** | [repository](https://github.com/tcp-acceleration-service/FlexTOE) · [benchmark](https://www.usenix.org/system/files/nsdi22-paper-shashidhara.pdf) |

## Verdict

NSDI'22, on two 20-core Xeon Gold 6138 hosts: FlexTOE on an Agilio CX40 40G NIC was compared with Linux kernel TCP, TAS (run on an Intel XL710 because of Agilio's slow DPDK driver) and the Chelsio T62100 kernel TOE, using identical app binaries and DCTCP. Memcached throughput reached up to 5.5x Linux, 4.9x Chelsio and 1.6x TAS, with the Agilio compute-bound at 12 host cores. With 250 cycles/RPC, RPC receive throughput was up to 4x Linux and 5.3x Chelsio, and 99.99th-percentile RTT was 3.2x lower than Chelsio. Firmware was built with NFP toolchain 6.1.0.1; the paper gives no host compiler flags, but the repo Makefiles use -O3 for host code and nfcc -O2 for firmware.

## Use it when

- You already run Netronome Agilio CX (NFP-4000) NICs and host CPU cycles spent in TCP limit a small-request server such as Memcached (32 B keys and values over persistent connections): up to 5.5x Linux and 1.6x TAS throughput.
- Tail latency matters more than median latency for small RPCs: 99.99th-percentile RTT is 3.2x lower than the Chelsio T6 TOE and 50% lower than TAS.
- You need existing POSIX-socket TCP binaries (not a new RPC API) to shed host TCP cost, and a few hundred to \~2K long-lived IPv4 connections fit in the NIC's CLS flow cache.
- Lossy fabrics with pipelined small RPCs: at 2% loss, 64 B echo throughput is at least 2x TAS and an order of magnitude above Linux and Chelsio.
- Research on programmable transport: the data path is split into C/NFP-assembly modules, so congestion-control or data-path changes need no ASIC respin.

## Skip it when

- Without an Agilio NFP-4000/6000 NIC (commodity NICs, cloud VMs, ARM hosts): the firmware and driver target only that hardware. The x86 and BlueField ports from the paper are not in this repo.
- Median-latency-bound single small RPCs: 20 us median vs 14 us for Chelsio and 16 us for TAS (&lt;256 B messages), because the multi-core NIC pipeline adds hops.
- Many thousands of connections with little data in flight: TAS is 1.5x faster in the connection-scalability test, throughput drops 24% at 8K connections, and flow state is capped at 16,384 flows at compile time (FLEXNIC_PL_FLOWST_NUM).
- Bulk streaming on lossy links or unidirectional large transfers: recovery is go-back-N with one out-of-order interval and no SACK, so Linux tolerates higher loss. Chelsio is 20% faster on unidirectional large RPCs.
- Anything needing maintenance or vendor support: the code was released once in Feb 2022, and firmware builds depend on a proprietary NFP SDK pinned to toolchain 6.1.0.1.

## How it is fast

Offload removes almost all host TCP work: in the paper's Memcached profile the host spends 1.67k cycles per request, vs 3.34k for TAS, 8.89k for the Chelsio TOE and 12.13k for Linux. On the NIC, the data path is split into a pipeline (pre-processing, protocol, post-processing, DMA, context queue) mapped onto the NFP's wimpy 800 MHz flow-processing cores. Only the per-connection protocol stage is atomic. The other stages are replicated, and the whole pipeline is replicated across 4 flow-groups chosen by a 4-tuple hash, with segment sequencing and reordering (the NFP GRO block) to keep TCP in order. Near-memory hardware adds CAM-backed 16-entry LRU flow caches, an IMEM CRC-32 lookup table for connections, and a Carousel time-wheel scheduler on EMEM hardware queues. The paper's ablation credits pipelining with 46x over run-to-completion, 8 hardware threads with 2.25x, stage replication with 1.35x and four flow-group islands with 2x.

## Compared with alternatives

Choose FlexTOE over Shenango or Demikernel only when you have Agilio NICs and want TCP processing off the host cores entirely rather than on dedicated kernel-bypass cores. Choose it over eRPC when applications must keep POSIX TCP sockets instead of adopting a new RPC API. The HTTP frameworks listed (Drogon, H2O, Lwan, etc.) sit above the transport and are not alternatives; FlexTOE was never benchmarked with an HTTP workload.

## Integration

| | |
|---|---|
| **Form** | shared lib (libflextoe_interpose.so socket shim, plus libflextoe_sockets.so and a low-level libflextoe.so) + user-space control-plane daemon + out-of-tree UIO kernel module (flextoe_uio.ko) + NFP firmware (fastpath.fw); all built from source with make |
| **Dependencies** | Netronome Agilio SmartNIC (NFP-4000/6000) with the out-of-tree nfp driver, Board Support Package and private NFP SDK/toolchain (nfcc/nfas/nfld under /opt/netronome); uio module; 1G hugepages mounted at /dev/hugepages-1048576kB; pthread, librt, libdl, libm |
| **Minimum toolchain** | Firmware: NFP toolchain 6.1.0.1 exactly (6.4.0.24 fails to build, issue #4). Host: any \$(CC) (Makefiles use -g3 -O3 -Wall -pthread; no version stated). Linux kernel 4.8+. |
| **Platforms** | Linux on x86-64 hosts (the host code uses x86 rdtsc inline asm; an ARM host needs porting per issue #2) with an Agilio CX NIC (default CHIP nfp-4xxx-b0); single 40GbE port in the paper |
| **Thread safety** | Multi-threaded apps are supported: libTOE uses per-thread context queues and per-socket locks. Compile-time limit is 32 application contexts (FLEXNIC_PL_APPCTX_NUM). |
| **Drop-in for the baseline** | partial — unmodified binaries using AF_INET SOCK_STREAM sockets are served through the interposer .so (the README does not document how to attach apps), but IPv6/UDP fall through to the kernel and several socket features are stubbed or missing (see gotchas) |

## Gotchas

- The socket shim is incomplete: EPOLLET is silently masked to level-triggered, epoll_pwait returns EINVAL ('TODO'), sendfile hits assert("NYI"), SO_RCVBUF/SO_SNDBUF always report 1 MiB, TCP_NODELAY and SO_REUSEADDR are always on, and send paths may block on non-blocking sockets (TODO in transfer.c).
- Features in the paper are not in the public repo: no XDP/eBPF, tracepoint, tcpdump or connection-splicing code. The x86 and BlueField pipeline ports live only on the 'pipeline' and 'bluefield-aarch64-pipeline' branches of the author's TAS fork (rajathshashidhara/tas).
- Defaults are small and memory must be pinned: per-flow RX/TX buffers default to 8 KiB (--tcp-rxbuf-len/--tcp-txbuf-len), link bandwidth defaults to 40 Gbps, and socket buffers come from physically contiguous 1G hugepages (no IOMMU support). The NIC ACKs every segment (no delayed ACK), which quadruples packet rate on bidirectional bulk flows.
- Bring-up is fragile: MAC-initialisation failures ('Service processor busy!') needed an NFP flash update or reboot (issue #1). The project site docs/index.html says the 3.2x tail cut is 'versus TAS', but the paper says 3.2x vs Chelsio and 50% vs TAS.

## Known shortcomings

- Needs an Agilio SmartNIC for TCP offload. Median latency is higher than Chelsio/TAS (20 vs 14-16 us) and TAS scales connections 1.5x better; the 2.4x/4x figures are against TAS, the 5.5x against Linux. No benchmark code in the repo; abandoned since 2022-02.
- A TCP transport offload, not an HTTP server; never benchmarked with HTTP. Paper features missing from the repo (XDP/eBPF, tracepoints, tcpdump, connection splicing); the x86 and BlueField ports live only in branches of rajathshashidhara/tas. Firmware needs the private Netronome NFP SDK (#3) and fails on toolchain 6.4.0.24 (works on 6.1.0.1, #4). Socket shim intercepts only AF_INET SOCK_STREAM, masks EPOLLET, epoll_pwait returns EINVAL, sendfile asserts NYI. Hard limits: 16,384 flows, 32 app contexts, 8 KiB per-flow buffers. Project site misstates the 3.2x tail-latency cut as versus TAS (it is versus Chelsio).

## Caveats and trade-offs

FlexTOE needs a Netronome Agilio (NFP-4000/6000) SmartNIC and 1G hugepages; the x86 and BlueField ports are described in the paper's appendix E but no separate port or benchmark directory is visible in the repo tree. It trades median latency for tail latency and throughput (20 us median vs 14-16 us for Chelsio/TAS), and TAS beats it by 1.5x on connection scalability. TAS ran on an Intel XL710 because of a slow Agilio DPDK driver. The category fit is a TCP offload engine rather than an HTTP server. The TAS baseline is an academic stack; the Linux kernel TCP stack is the recognizable incumbent (up to 5.5x Memcached throughput).

Requires a Netronome Agilio SmartNIC; programmability via C/eBPF/XDP adds development complexity vs. a plain sockets server; unmaintained since 2022

## Maintenance

Abandoned research code: a single public release, last commit 2022-02-27, 4 issues all closed (maintainer still answered in Feb 2025). The code is BSD-3-Clause, and some Netronome-derived build files carry Apache-2.0/BSD-2-Clause headers. It cannot be built without Agilio hardware and the private NFP SDK, so it is not realistically vendorable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed NSDI'22 paper measures FlexTOE head-to-head against the Linux kernel TCP stack, TAS and the Chelsio T6 TOE on the same testbed (Xeon Gold 6138 hosts) and shows wins. It is not A: the repo has no benchmark code (no memtier/RPC benchmark directory) and the host compiler and flags are never stated (only 'NFP compiler toolchain 6.1.0.1' for the SmartNIC firmware).
- **Verifier notes:** The abstract numbers are exact on arXiv and in the NSDI'22 PDF (both opened). benchmark_url now points at the full NSDI PDF, which also holds the Linux-baseline figures. gh confirms BSD-3-Clause, not archived, not a fork, 62 stars, last commit 2022-02-27, so abandoned is correct.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2110.10919>
  - <https://www.usenix.org/system/files/nsdi22-paper-shashidhara.pdf>
  - <https://github.com/tcp-acceleration-service/FlexTOE>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/README.md>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/Makefile>
  - <https://tcp-acceleration-service.github.io/FlexTOE/>
- **Sources the enricher read:**
  - <https://github.com/tcp-acceleration-service/FlexTOE>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/README.md>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/Makefile>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/user/Makefile>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/Makefile>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/sockets/Makefile>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/tas/Makefile>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/Makefile>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/Makefile.nfp.config>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/pipeline.h>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/config.h>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/preprocess.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/flows.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/qman.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/firmware/packet_defs.h>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/include/params.h>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/include/rte/cycles.h>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/include/rte/hash_crc.h>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/sockets/interpose.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/sockets/control.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/sockets/epoll.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/lib/sockets/transfer.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/user/cc.c>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/scripts/load_fw.sh>
  - <https://github.com/tcp-acceleration-service/FlexTOE/blob/main/docs/index.html>
  - <https://github.com/tcp-acceleration-service/FlexTOE/issues/1>
  - <https://github.com/tcp-acceleration-service/FlexTOE/issues/2>
  - <https://github.com/tcp-acceleration-service/FlexTOE/issues/3>
  - <https://github.com/tcp-acceleration-service/FlexTOE/issues/4>
  - <https://github.com/rajathshashidhara/tas/tree/pipeline>
  - <https://github.com/rajathshashidhara/tas/tree/bluefield-aarch64-pipeline>
  - <https://www.usenix.org/system/files/nsdi22-paper-shashidhara.pdf>
  - <https://www.usenix.org/conference/nsdi22/presentation/shashidhara>
  - <https://arxiv.org/abs/2110.10919>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/tcp-acceleration-service/flextoe`) · [data/wave5/enrich/raw/github_com_tcp_acceleration_service_flextoe.json](../../../data/wave5/enrich/raw/github_com_tcp_acceleration_service_flextoe.json) (enrichment confidence 0.8)

</details>
