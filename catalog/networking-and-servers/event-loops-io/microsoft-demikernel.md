# Demikernel

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust kernel-bypass library OS with a zero-copy, queue-based socket API over DPDK; 4-5x lower echo RTT than Linux sockets.

| | |
|---|---|
| **Beats** | Linux kernel sockets networking path |
| **Claimed result** | SOSP'21 paper, 64 B echo RTT on Linux hosts (Fig. 5): Linux POSIX 30.4 us vs Catnip (DPDK) UDP 6.0 us + 0.025 us of Demikernel time, Catnip TCP 7.1 + 0.053 us, Catmint (RDMA) 5.3 + 0.949 us. That is about 4.3-5x lower RTT with Catnip (derived from page data). UDP relay server (Fig. 10): average 24.9 us on Linux vs 13.9 us on Catnip, p99 27.6 vs 14.9 us; the paper says 'Catnip reduces the server-side latency per request by 11us on average and 13.7us at the p99' (io_uring: 24.4/25.8 us). Redis in-memory peak throughput vs unmodified Redis on Linux (Fig. 11): 'Catmint gives 2x throughput, and Catnip offers 20% better throughput'. Azure VM: 'Catnip offers a 5x latency improvement over the Linux kernel'. The 2019 first-party blog (CloudLab Redis) says '60% of the latency comes from the OS kernel and its interface' (30% from interface inefficiency, another 30% removed by RDMA/DPDK kernel bypass). |
| **Workload** | SOSP'21: 64 B echo server/client (1M echos, 5 runs); UDP relay (TURN) server driven by a Linux traffic generator; Redis via redis-benchmark GET/SET (64 B values, 1M keys, in-memory and with a per-SET fsync append-only log); TxnStore under YCSB-t. Compared against Linux POSIX sockets/epoll, io_uring and kernel-bypass systems (eRPC, Shenango, Caladan, DPDK testpmd, RDMA perftest). The 2019 blog ran the Redis benchmark on CloudLab. |
| **Metric** | latency |
| **Hardware** | SOSP'21 Linux cluster: 5 servers with 20-core dual-socket Intel Xeon Silver 4114 @ 2.2 GHz, Mellanox CX-5 100 Gbps NICs, Arista 7060CX 100 Gbps switch, Intel Optane 800P NVMe. Windows cluster: 14-core dual-socket Xeon 2690 @ 2.6 GHz with Mellanox CX-4 56 Gbps. The 2019 blog used CloudLab with a 25Gb network and Mellanox CX-4 NICs. |
| **Adoption** | 1,238 stars |
| **Last commit** | 2025-11-12 |
| **Links** | [repository](https://github.com/microsoft/demikernel) · [benchmark](https://irenezhang.net/papers/demikernel-sosp21.pdf) |

## Verdict

In the open-access SOSP'21 paper (Xeon Silver 4114 at 2.2 GHz, Mellanox CX-5 100 GbE, Arista switch; Linux tuned with pinned cores, real-time priority and the performance governor), a 64 B echo averaged 30.4 us RTT over POSIX sockets vs 6.0 us for Catnip UDP and 7.1 us for Catnip TCP (about 4.3-5x). A TURN UDP relay fell from 24.9/27.6 us (average/p99) to 13.9/14.9 us, and Redis in-memory peak throughput rose 20% with Catnip (2x with the RDMA LibOS). The paper gives no compiler version or flags, and the RDMA (Catmint) and SPDK (Cattree) LibOSes behind the 2x Redis and disk-logging results are no longer in the repository.

## Use it when

- Microsecond-scale RPC, key-value cache or UDP relay servers on bare-metal or Azure hosts with Mellanox ConnectX-4/5/6 NICs and DPDK, where a 64 B round trip of about 6-7 us instead of about 30 us through the kernel matters.
- Single-core, run-to-completion servers where you can dedicate a spinning core per instance and structure the main loop as pop, then wait_any, then push.
- Apps that should run unchanged on plain Linux or Windows sockets (catnap) for development and CI, and switch to DPDK (catnip) in production by rebuilding with LIBOS=catnip.
- Porting an epoll event loop (Redis-style) when you want zero-copy sends from the app heap without writing your own reference counting for in-flight buffers.

## Skip it when

- Multi-core scaling: each thread gets its own thread-local LibOS, catnip configures one RX and one TX queue, and multi-core support is still open (issue #78).
- Throughput-bound work: in the paper Catnip (UDP) reached 70% of Caladan's peak throughput, and catnap gave 75-80% lower Redis peak throughput than stock Redis because it spends a core polling.
- Protocol coverage: IPv6 (#935), IP fragmentation (#208), SACK (#183), TCP timestamps (#182), INADDR_ANY (#189) and port 0 (#582) wildcards are all open issues, and delayed ACKs and the ISN generator also have open issues.
- NICs other than Mellanox, or AArch64: the catnip build only selects the mlx4 or mlx5 driver, other NICs need changes to device code (#317, #1590), and the DPDK bindings fail to build on AArch64 because of an unconditional -mavx flag (#1631).
- Many connections at high load: open confirmed bug #862 reports catnip panicking with 'failed to clone mbuf' when the DPDK mempool runs out (reported at about 150K req/s over 100 connections).

## How it is fast

Catnip takes the kernel out of the data path. A DPDK poll-mode driver (rte_eth_rx_burst/tx_burst on a single RX/TX queue) feeds a user-level TCP stack (RFC 793/7323, Cubic congestion control) and UDP stack, and the whole request runs to completion on one core. I/O is zero-copy. Application buffers come from a DMA-capable pool (DPDK mbufs wrapped in reference-counted DemiBuffers). Push hands ownership to the stack, and use-after-free protection lets the app free a buffer right after pushing it. The paper measures Catnip's overhead at about 125 ns per UDP packet and 200 ns per TCP packet. Cooperative Rust async coroutines replace threads and interrupts, under a single-threaded scheduler that keeps readiness bits for 64 tasks per word so it can skip blocked ones. Even catnap cuts some latency by busy-polling epoll_wait with a zero timeout instead of sleeping.

## Compared with alternatives

Pick Demikernel over Shenango or eRPC when you want one sockets-like TCP/UDP API that also runs on plain Linux and Windows sockets, and single-core zero-copy latency matters more than peak throughput. In the SOSP'21 echo test Catnip was 3.1 us faster than Shenango but 1.7 us slower than Caladan, and eRPC was 0.2 us faster than the RDMA LibOS. Drogon, H2O, Lwan and the other siblings are HTTP servers on kernel sockets; Demikernel has no HTTP layer at all.

## Integration

| | |
|---|---|
| **Form** | crate (rlib) and shared lib (cdylib with C headers in include/demi), built through make |
| **Dependencies** | catnip needs DPDK (scripts/build-install-dpdk.sh), a Mellanox mlx4 or mlx5 PMD, 2 MB hugepages and root. All LibOSes need a YAML config with local IP, MAC, interface, a static ARP table and, for DPDK, the NIC's PCI address. Windows catpowder needs XDP bindings. Rust crates include mimalloc (installed as the global allocator), futures, socket2, crossbeam-channel, flexi_logger, yaml-rust and x86. |
| **Minimum toolchain** | Rust nightly (rust-toolchain pins nightly-2025-02-17; uses #![feature(allocator_api, hash_extract_if, test)]), edition 2021. Setup is documented for Ubuntu 22.04. |
| **Platforms** | Linux x86-64 (catnap, catnip on Mellanox ConnectX with DPDK, catpowder via AF_PACKET) and Windows (catnap Winsock, catpowder XDP). The catnip build is broken on AArch64 (#1631), and there is no macOS support (#1506 open). |
| **Thread safety** | Single-threaded by design: the LibOS is stored in a thread_local, demi_init initializes it per thread, the scheduler is documented as single-threaded, and catnip sets MLX5_SINGLE_THREADED. Whether several threads can each run their own catnip instance is not documented. |
| **Drop-in for the baseline** | partial — the setup calls (socket, bind, listen, setsockopt) mirror POSIX, but the data path is asynchronous push/pop with queue tokens and library-allocated scatter-gather buffers, so read/write/epoll loops must be rewritten |

## Gotchas

- demi_push is zero-copy: do not modify or free the scatter-gather memory until the push token completes. Use-after-free protection only delays a free and does not stop writes. Every SGA returned by pop must be freed with demi_sgafree.
- demi_wait and demi_wait_any spin the calling thread, and catnap polls epoll with a zero timeout, so an idle server still uses 100% of a core. The paper notes this for catnap even with a single client.
- Size limits: demi_sgaalloc fails above 64 KB (16-bit length, #1133), POP_SIZE_MAX is 8192 bytes, and an SGA holds at most 20 segments.
- Linking the Rust crate makes mimalloc your process's #[global_allocator] (src/lib.rs), which conflicts with any allocator you set yourself. The demi_init man page still documents an old argc/argv signature, while the header takes a demi_args struct.

## Known shortcomings

- Kernel-bypass library OS needing DPDK or RDMA NICs and applications ported to its API; competitive with, not faster than, other bypass stacks such as Caladan and eRPC. No toolchain or flags stated.
- Only the Catnip (DPDK) numbers apply to today's code: the RDMA (Catmint) and SPDK (Cattree) LibOSes behind the '2x Redis' and storage results are gone, and Catnap is now Rust. catnip panics with 'failed to clone mbuf' when the mempool runs out at \~150K req/s (#862); AArch64 build fails on -mavx (#1631); effectively Mellanox-only (#317, #1590); single RX/TX queue, no multi-core (#78); no IPv6, fragmentation, SACK or TCP timestamps. Last commit 2025-11, last crate release 2024-09. Needs pinned nightly Rust and makes mimalloc the global allocator; demi_sgaalloc fails above 64 KB (#1133).

## Caveats and trade-offs

The SOSP'21 paper is open access at the first author's site; the ACM DL PDF returned HTTP 403 to automated fetches, but the paper is not paywalled. The wins are against the Linux kernel sockets/epoll path. Against other kernel-bypass stacks Demikernel is competitive rather than uniformly faster: Catnip echo is 1.7 us slower than Caladan, Catnip (UDP) reaches 70% of Caladan's peak throughput, and Catmint reaches 46% of eRPC's. The Linux-sockets LibOS (Catnap) busy-polls a full core and has lower Redis peak throughput than unmodified Redis. The gains need DPDK/RDMA-capable NICs, and the README calls the project a prototype with no guarantees. The paper states no Rust/compiler version or build flags.

Project explicitly labeled a research prototype with 'no guarantees'; requires DPDK/RDMA hardware for the kernel-bypass LibOSes (catnip); Linux-socket LibOS (catnap) has no bypass benefit by itself

## Maintenance

MIT-licensed Microsoft Research prototype that the README says comes with 'no guarantees'. The dev branch last changed on 2025-11-12, the crates.io release is 1.5.13 from September 2024, and a roadmap question (#1632) has no answer; treat it as vendorable research code, not a supported product.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. The peer-reviewed SOSP'21 paper is open access (author-hosted PDF) and reports numeric wins against the Linux kernel sockets/epoll path: echo RTT, UDP relay latency, Redis throughput and an Azure VM run. Hardware is stated (Xeon Silver 4114, Mellanox CX-5) and the code is public on GitHub, but the paper gives no compiler/toolchain version or build flags, so it is not A.
- **Verifier notes:** Upgraded C-&gt;B through the open-access SOSP'21 paper, which has concrete numbers vs Linux: about 5x echo RTT, 2x Redis throughput with RDMA, and 5x on an Azure VM. The blog's 30%/60% figures are quoted correctly. Metadata checked: MIT, 1,238 stars, last default-branch (dev) commit 2025-11-12, so 'active' holds; the repo pushed_at of 2026-07-23 comes from a non-default branch.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <http://irenezhang.net/blog/2019/05/21/demikernel.html>
  - <https://irenezhang.net/papers/demikernel-sosp21.pdf>
  - <https://irenezhang.net/papers/demikernel-hotos19.pdf>
  - <https://dl.acm.org/doi/pdf/10.1145/3477132.3483569>
  - <https://github.com/microsoft/demikernel>
- **Sources the enricher read:**
  - <https://github.com/microsoft/demikernel>
  - <https://github.com/microsoft/demikernel/blob/dev/README.md>
  - <https://github.com/microsoft/demikernel/blob/dev/Cargo.toml>
  - <https://github.com/microsoft/demikernel/blob/dev/rust-toolchain>
  - <https://github.com/microsoft/demikernel/blob/dev/linux.mk>
  - <https://github.com/microsoft/demikernel/blob/dev/doc/building.md>
  - <https://github.com/microsoft/demikernel/blob/dev/doc/setup.md>
  - <https://github.com/microsoft/demikernel/blob/dev/doc/testing.md>
  - <https://github.com/microsoft/demikernel/blob/dev/include/demi/libos.h>
  - <https://github.com/microsoft/demikernel/blob/dev/include/demi/wait.h>
  - <https://github.com/microsoft/demikernel/blob/dev/include/demi/sga.h>
  - <https://github.com/microsoft/demikernel/blob/dev/man/demi_push.md>
  - <https://github.com/microsoft/demikernel/blob/dev/man/demi_pop.md>
  - <https://github.com/microsoft/demikernel/blob/dev/man/demi_wait.md>
  - <https://github.com/microsoft/demikernel/blob/dev/man/demi_init.md>
  - <https://github.com/microsoft/demikernel/blob/dev/man/demi_sgaalloc.md>
  - <https://github.com/microsoft/demikernel/blob/dev/src/lib.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/demikernel/bindings.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/demikernel/libos/mod.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/catnap/linux/transport.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/catnip/runtime/mod.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/catnip/runtime/mempool.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/catpowder/linux/rawsocket/rawsocket.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/runtime/mod.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/runtime/scheduler/scheduler.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/runtime/memory/demibuffer.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/runtime/limits.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/src/runtime/types/memory.rs>
  - <https://github.com/microsoft/demikernel/blob/dev/.github/workflows/catnip.yml>
  - <https://github.com/microsoft/demikernel/issues>
  - <https://github.com/microsoft/demikernel/issues/78>
  - <https://github.com/microsoft/demikernel/issues/317>
  - <https://github.com/microsoft/demikernel/issues/862>
  - <https://github.com/microsoft/demikernel/issues/1133>
  - <https://github.com/microsoft/demikernel/issues/1590>
  - <https://github.com/microsoft/demikernel/issues/1631>
  - <https://github.com/microsoft/demikernel/issues/1632>
  - <https://github.com/microsoft/demikernel/issues/1634>
  - <https://github.com/microsoft/demikernel/issues/1637>
  - <https://github.com/microsoft/demikernel/commits/dev>
  - <https://irenezhang.net/papers/demikernel-sosp21.pdf>
  - <http://irenezhang.net/blog/2019/05/21/demikernel.html>
  - <https://crates.io/api/v1/crates/demikernel>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/microsoft/demikernel`) · [data/wave5/enrich/raw/github_com_microsoft_demikernel.json](../../../data/wave5/enrich/raw/github_com_microsoft_demikernel.json) (enrichment confidence 0.72)

</details>
