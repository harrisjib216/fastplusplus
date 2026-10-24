# OpenOnload (with ef_vi and TCPDirect kernel-bypass APIs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0 AND BSD-2-Clause` · 🟢 active

> AMD's user-level TCP/UDP stack that accelerates unmodified BSD-sockets apps by bypassing the Linux kernel network stack.

| | |
|---|---|
| **Beats** | Linux kernel UDP sockets (kernel network stack) |
| **Claimed result** | Average latency over report lines 2-6: 14.24-14.72 us with Onload vs 19.44-20.20 us without, about 1.37x lower (derived from page data); packets per second 64635-66688 vs 47340-49298. The first report line (14.303 vs 20.310 us) covers a partial first interval in which the client's stats struct is calloc'd rather than initialised (min shows 0.000 us), so lines 2-6 are the cleaner figures. |
| **Workload** | majek/dump udpclient/udpserver UDP ping-pong, 32-byte payload (PKT_SIZE in udpclient.c), one session per side, with and without Onload acceleration. |
| **Metric** | latency |
| **Hardware** | Two servers back-to-back with Solarflare X2522 NICs (single channel mode, isolcpus and kernel parameter tuning, EF_POLL_USEC=100000 latency profile); OpenOnload 7.1.1.75 per the pasted output; CPU model and kernel version not stated. |
| **Adoption** | 851 stars |
| **Last commit** | 2026-10-23 |
| **Links** | [repository](https://github.com/Xilinx-CNS/onload) · [benchmark](https://github.com/Xilinx-CNS/onload/issues/28) |

## Verdict

A user on issue 28 (Mar 2022) ran majek/dump udpclient/udpserver (32-byte UDP payload, --polling with MSG_DONTWAIT recv, client pinned with taskset) between two back-to-back servers with Solarflare X2522 NICs and Onload 7.1.1.75 with the latency profile: average RTT about 14.2-14.7 us with Onload vs 19.4-20.3 us through Linux kernel sockets, roughly 1.37x lower on the five steady-state lines (derived from page data), with min RTT about 8.9-9.2 us vs 12.2-12.7 us. CPU model, kernel version and whether the server side also ran under Onload are not stated; on AWS ENA with AF_XDP, issue 139 measured Onload slower than the kernel.

## Use it when

- Latency-sensitive UDP or TCP request/response on AMD Solarflare X2522/X3522/X4 or SFN8000-series NICs where you cannot rewrite the application (trading, market data, RPC fan-out).
- Apps that call recv/poll/epoll in a tight loop and can afford one or more dedicated busy-polling cores per stack.
- Small-message ping-pong where kernel syscall and interrupt overhead dominate: the one public user measurement (32-byte UDP payload) showed about 14.2-14.7 us vs 19.4-20.3 us average RTT.
- Epoll servers managing many sockets on AF_XDP-capable NICs (Intel ixgbe/i40e, Mellanox ConnectX-4 Lx+), which is where the maintainers say AF_XDP mode helps.
- Hot UDP paths you are willing to hand-code on ef_vi (raw frames, zero copy) while leaving TCP to Onload in the same process.

## Skip it when

- Cloud VMs without Solarflare hardware: on AWS ENA in AF_XDP mode a user measured median 47.9 us with Onload vs 42.7 us with the kernel (issue 139), and others saw no gain or \~1 us worse (issue 28).
- Throughput-bound bulk transfer or apps with separate reader and writer threads on one socket: iperf3 dropped from \~9 to \~5 Gb/s on ixgbe AF_XDP (issue 306), and the maintainer notes iperf's two threads cause stack-lock contention.
- Hosts where you cannot load out-of-tree kernel modules, need non-x86_64 (released versions support amd64 only), or run kernels outside the tested range (repo head targets 6.1-7.0).
- Deployments that need production-quality support on non-Solarflare NICs: the README calls AF_XDP mode a community work in progress, not release quality.
- Energy- or core-constrained machines: the latency profile spins each blocking call for up to 100 ms (EF_POLL_USEC=100000), so every waiting thread burns a core.

## How it is fast

Kernel bypass: the protocol stack runs in user space with direct access to NIC descriptor rings and event queues, so the data path needs no system calls and no kernel/user copies. Blocking calls busy-poll the NIC (EF_POLL_USEC=100000 in the latency profile spins up to 100 ms before sleeping), avoiding interrupt and wakeup latency. On AMD Solarflare X2/X3/X4 adapters it can use PIO and CTPIO cut-through transmit (latency-best profile) so a frame starts on the wire before it is fully DMA'd. On other NICs it falls back to Linux AF_XDP, where the maintainers say latency is not expected to improve.

## Compared with alternatives

Pick Onload over mTCP, F-Stack or Demikernel when you must accelerate an unmodified sockets binary and already run AMD Solarflare NICs; those stacks need porting to their own APIs or DPDK. Pick io_uring-based loops such as monoio or the Asio io_uring backend instead when you lack Solarflare hardware or cannot load vendor kernel modules.

## Integration

| | |
|---|---|
| **Form** | shared lib (LD_PRELOAD via the `onload` launcher) plus kernel modules; ef_vi as a library; built from source, DKMS/RPM/DEB packaging scripts provided |
| **Dependencies** | Linux kernel headers for the target kernel, gcc and g++, libcap-devel, libmnl-devel, binutils/gawk/make/perl-Test-Harness; an AMD Solarflare adapter for native ef_vi mode or an AF_XDP-capable driver otherwise |
| **Minimum toolchain** | C11, builds with gcc-11 (EL9); repo head lists kernels 6.1-7.0 (Debian 12+, Ubuntu 24.04+, EL 9/10); release 9.2.x lists kernels 5.11-7.0 |
| **Platforms** | Linux x86_64 only (released versions; eflatency hard-requires x86_64); best on AMD Solarflare SFN8522/8542/8042, X2522, X2541, X3522, X4; other NICs via AF_XDP |
| **Thread safety** | Sockets keep BSD semantics behind a per-stack lock, but concurrent calls on one stack contend; the latency-best profile sets EF_EPOLL_MT_SAFE=1, which assumes no concurrent calls on a single epoll object. Open issues report multithreading problems in ci_tcp_sendmsg (#333) and a deadlock in eplock_slow (#289). |
| **Drop-in for the baseline** | partial — binary compatible with sockets apps via the onload launcher (no recompile), but needs its own kernel modules, root to install, a supported NIC and tuning; ef_vi and TCPDirect need code written to their own APIs |

## Gotchas

- Profiles change semantics: latency-best enables CTPIO cut-through (can emit poisoned frames on X2 above 10GbE), EF_CTPIO_SWITCH_BYPASS (incompatible with multicast loopback) and EF_EPOLL_MT_SAFE=1.
- Host configuration can erase the gain: a user on a Ryzen 9950X3D with X2522 saw \~250 us latency spikes traced to a stray `pcie_aspm=off` kernel parameter (issue 272, closed).
- AF_XDP mode needs driver XDP_REDIRECT support, often a single combined queue and ntuple filters (or enable_af_xdp_flow_filters=0); several ENA/ixgbevf users never got it working.
- The public repo is community-supported and expects you to run git head; supported releases and the UG1586 user guide come from AMD.

## Known shortcomings

- Only numbers are one user comment on issue 28 (X2522, average 20.31 vs 14.30 us, OpenOnload 7.1.1.75, six lines per side, no CPU or kernel); the \~3.5 us figure is the minimum-latency gap, not the average. Issue 139: AF_XDP on AWS slower (47.883 vs 42.735 us median).
- first report line uses an uninitialised stats interval; lines 2-6 give about 1.37x, not 1.42x

## Caveats and trade-offs

The only numbers reachable are a GitHub issue comment by a user (issue 28, 8 Mar 2022): six report lines per side from one session, no CPU model, kernel or packet size, so tier C. The issue itself is about non-Solarflare adapters; this comment's numbers are on Solarflare X2522 NICs. The same issue has another user reporting Onload about 1 us slower than kernel sockets on AWS ENA (2 Mar 2022) and a third seeing no difference on ENA; a further commenter claims 'Redis: 2X' and 'Memcached: 35% better' vs kernel over AF_XDP on Mellanox/Intel NICs with no methodology. Issue 139 (opened 20 Apr 2023, AWS m5zn.12xlarge, AF_XDP mode, custom UDP ping-pong) measured median 47.883 us with Onload vs 42.735 us with the kernel (Onload slower); a maintainer replied that latency is not expected to benefit from AF_XDP Onload at all and that it helps applications using epoll to manage many sockets. The README, README.ef_vi and the sibling TCPDirect README contain no numbers. Vendor user guide (UG1586) and the slide deck seen in a search snippet (reported half RTT TCP 11.2 us kernel vs 5.3 us Onload) could not be opened (host blocked); snippet only, not used for the tier. Benefit depends strongly on NIC, driver and tuning. [retier] Enricher: majek/dump's udpclient callocs its stats struct without stddev_init, so the first report line (the record's earlier headline) mixes a partial interval; lines 2-6 give about 1.37x (derived from page data). Payload is 32 B. Other reports: issue 306 (iperf3 on an ixgbe AF_XDP NIC fell from 9 to 5 Gb/s under Onload); issue 272 (latency spikes traced to a stray pcie_aspm=off); the latency-best profile sets EF_EPOLL_MT_SAFE=1 and CTPIO cut-through, so results depend on profile and NIC.

Best results need AMD Solarflare NICs (ef_vi native); other NICs use community-supported AF_XDP mode that is not release quality. Kernel modules plus a user-space library that intercepts socket calls, busy-polling cores (EF_POLL_USEC=100000 in the default latency profile per the issue), dual GPLv2.0 and BSD-2-Clause licensing, supported releases come from the vendor. ef_vi and TCPDirect require porting to their own APIs and, for ef_vi, a user-written protocol stack.

## Maintenance

Actively maintained by AMD (commits on 23 Oct 2026, release 9.2.1 in the tree); GPLv2 overall with ef_vi, the control plane and examples under BSD-2-Clause, so the ef_vi pieces are copyable while the stack itself carries GPL obligations.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Issue 28 comment (aneagoe, 8 Mar 2022) shows udpclient output from majek/dump with and without the onload launcher on X2522 NICs (avg 20.310 vs 14.303 us, pps 47340 vs 65540); public tool but no CPU model, kernel or compiler and no well-known suite or paper, so C; the README has no numbers.
- **Verifier notes:** Issue 28 and 139 numbers confirmed verbatim; original caveat said 'one run shown' but six lines per side are posted, and the Onload version (7.1.1.75) appears in the pasted output. Metadata: 851 stars, GPLv2 and BSD-2-Clause per README, last commit 2026-10-23, not archived. README.ef_vi and TCPDirect README not reopened by me.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-83 (wave 5 book seed pass, 2026-10-24); enrichment (wave 5 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/Xilinx-CNS/onload>
  - <https://github.com/Xilinx-CNS/onload/commits>
  - <https://github.com/Xilinx-CNS/onload/issues/28>
  - <https://github.com/Xilinx-CNS/onload/issues/139>
- **Sources the enricher read:**
  - <https://github.com/Xilinx-CNS/onload>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/README.md>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/DEVELOPING.md>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/src/onload/distfiles/LICENSE>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/src/onload/distfiles/README>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/src/onload/distfiles/README.ef_vi>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/src/onload/distfiles/ReleaseNotes>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/src/onload/distfiles/ChangeLog>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/scripts/onload_profiles/latency.opf>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/scripts/onload_profiles/latency-best.opf>
  - <https://raw.githubusercontent.com/Xilinx-CNS/onload/HEAD/src/tests/ef_vi/eflatency.c>
  - <https://github.com/Xilinx-CNS/onload/tree/master/src>
  - <https://github.com/Xilinx-CNS/onload/commits/master>
  - <https://github.com/Xilinx-CNS/onload/issues/28>
  - <https://github.com/Xilinx-CNS/onload/issues/28#issuecomment-1061840796>
  - <https://github.com/Xilinx-CNS/onload/issues/139>
  - <https://github.com/Xilinx-CNS/onload/issues/272>
  - <https://github.com/Xilinx-CNS/onload/issues/306>
  - <https://github.com/Xilinx-CNS/onload/issues?q=is%3Aissue+latency+OR+crash+OR+performance>
  - <https://raw.githubusercontent.com/Xilinx-CNS/tcpdirect/HEAD/README.md>
  - <https://raw.githubusercontent.com/majek/dump/master/how-to-receive-a-packet/udpclient.c>
  - <https://raw.githubusercontent.com/majek/dump/master/how-to-receive-a-packet/udpserver.c>
  - <https://raw.githubusercontent.com/majek/dump/master/how-to-receive-a-packet/stddev.h>
  - https://docs.amd.com/r/en-US/ug1586-onload-user/EF_EPOLL_MT_SAFE (search snippet only)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/xilinx-cns/onload`) · [data/wave5/enrich/raw/github_com_xilinx_cns_onload.json](../../../data/wave5/enrich/raw/github_com_xilinx_cns_onload.json) (enrichment confidence 0.7)

</details>
