# IX (protected dataplane OS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `MIT` · 🔴 abandoned

> Protected dataplane OS that runs TCP/IP and one app on dedicated polling cores; 2.8-3.6x memcached throughput over Linux+epoll.

| | |
|---|---|
| **Beats** | Linux 3.16.1 kernel TCP stack via libevent + epoll: stock memcached-1.4.18 on tuned Linux (pinned threads, IRQ affinity, tuned interrupt moderation); mTCP is a second baseline in the microbenchmarks |
| **Claimed result** | Abstract: IX 'improves the throughput of a widely deployed, key-value store by up to 3.6x and reduces tail latency by more than 2x'. Sec 5.5 / Table 2 (memcached vs Linux): 2.8x (ETC, 550K -&gt; 1550K RPS) and 3.6x (USR, 500K -&gt; 1800K RPS) at a 500us 99th-percentile SLA. Unloaded 99th-percentile latency is 94 -&gt; 45us (ETC) and 85 -&gt; 32us (USR). Microbenchmarks: up to 10x the throughput of Linux and 1.9x of mTCP for short messages on 10GbE; one-way 64B latency 5.7us vs 24us for Linux (4x). |
| **Workload** | memcached-1.4.18 ported to IX's libix event API vs stock memcached on Linux. The mutilate load generator ran Facebook ETC (20-70B keys, 1B-1KB values, 75% GET) and USR (&lt;20B keys, 2B values, 99% GET) workloads from 23 Linux client machines over 1,476 TCP connections. Metrics are max RPS at a 500us 99th-percentile SLA and unloaded 99th-percentile latency. The paper also has NetPIPE ping-pong, short-message echo and connection-scaling (up to 250K connections) microbenchmarks. |
| **Metric** | throughput |
| **Hardware** | Server: Intel Xeon E5-2665 @ 2.4 GHz (8 cores / 16 hyperthreads per socket), 256 GB DRAM, Intel x520 10GbE NICs (82599EB), either 1 port or 4x10GbE bonded. Clients: Xeon E5-2637 @ 3.5 GHz and E5-2650 @ 2.6 GHz running Linux. Switch: Quanta/Cumulus 48x10GbE (Broadcom Trident+). OS: Ubuntu 14.04 with the Linux 3.16.1 kernel. For memcached, Linux used 8 cores and IX used 6. |
| **Compiler and flags** | Not stated in the paper. The 2016 code release's build files show dp/Makefile building the IX dataplane with gcc -O3 -mno-red-zone -fno-pie, and ix-bench/Makefile building its libevent/epoll client/server with gcc -O2. No compiler version is given anywhere, and no memcached build flags are given. |
| **Adoption** | 136 GitHub stars, 39 forks (ix-project/ix) |
| **Last commit** | 2017-11-06 |
| **Links** | [repository](https://github.com/ix-project/ix) · [benchmark](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-belay.pdf) |

## Verdict

OSDI'14 paper: memcached-1.4.18 ported to libix on 6 cores vs. stock memcached (libevent+epoll) on 8 pinned, interrupt-tuned cores of Linux 3.16.1, on a Xeon E5-2665 @ 2.4 GHz server with Intel x520 (82599) 10GbE and 23 Linux mutilate clients over 1,476 connections. Max RPS within a 500us p99 SLA rose from 550K to 1,550K (ETC, 2.8x) and from 500K to 1,800K (USR, 3.6x), and unloaded p99 latency fell from 94 to 45us and from 85 to 32us; no compiler or version is given (the 2016 release builds the dataplane with gcc -O3).

## Use it when

- Reproducing or extending the OSDI'14/SoCC'15 results: ix-project/ix-bench holds the memcached, ping-pong, short-message and connection-scaling scripts, and the ported memcached (ix branch of ix-project/memcached) and the mutilate load generator are public under ix-project.
- Small-message TCP request/response servers (e.g. key-value GETs with &lt;20B keys and 2B values) where p99 latency under a few hundred microseconds sets capacity, on a dedicated server with Intel 82599/X520/X540 10GbE.
- High connection churn or many connections: the paper reports 3.8M TCP connections/s on 4x10GbE and runs up to 250K concurrent connections (at 250K, throughput falls to 47% of IX's peak from L3 cache misses).
- Research on kernel-bypass designs that keep the network stack isolated from application code (VT-x ring separation) while Linux remains the control plane.

## Skip it when

- Anything production or long-lived: no commits since 2017-11-06, DPDK pinned at 16.04, and the maintainer said in 2021 (issue #36) that Dune has not been updated and likely does not support recent kernels.
- Hardware or network setups outside its narrow support: non-Intel NICs (mlx4 was requested, never added, issue #24), machines without VT-x, non-x86, IPv6, SR-IOV, or more than one IX instance per host (issue #2).
- Untrusted or bursty peers: libix has no receive flow control, and one flooding connection can terminate the server process (issue #12).
- Applications that block in handlers or depend on POSIX sockets, TLS libraries or other socket-based code: every network path must be rewritten to ixev callbacks or the batched API.
- Lock-heavy or CPU-bound servers: IX only removes kernel network overhead; memcached gained less on ETC (2.8x) and stopped scaling past 6 cores on IX because of its own lock contention.

## How it is fast

Each elastic thread runs to completion: it polls its own NIC RX ring, pushes a bounded batch (default 64 packets) through an lwIP-derived TCP/IP stack, switches to the application to consume events, then executes the application's batched system calls, TCP timers and TX in the same loop, with no interrupts and no intermediate socket buffers. Batching is adaptive, so batches only grow under congestion and light load keeps latency low. RSS flow-consistent hashing gives each hyperthread its own RX/TX queue pair, flows and memory pools, so the common path takes no locks and causes no cache-coherence traffic. The dataplane also uses only 2MB pages, a hierarchical timing wheel, and refills RX descriptors 32 at a time to cut PCIe writes.

## Compared with alternatives

Pick IX over mTCP or F-Stack only when you need the TCP stack protected from application code (separate rings under VT-x) or are reproducing the OSDI'14 comparison, where IX delivered 1.9x mTCP's short-message rate and lower 64B latency. Arrakis is the closer research analogue and adds IOMMU/SR-IOV support that IX lacks; for anything you must run today, F-Stack or Seastar are the maintained DPDK stacks.

## Integration

| | |
|---|---|
| **Form** | static lib (libix.a) linked into the application, which runs under the dp/ix dataplane binary; plus Linux kernel modules (dune.ko, pcidma.ko, igb_uio.ko) and a control-plane script |
| **Dependencies** | DPDK 16.04 (git submodule; ixgbe/i40e PMDs, eal, mbuf, mempool, ring), Dune (dune.ko + libdune, ix-project/dune has no license file), pcidma, igb_uio/uio, libconfig, libnuma, 2MB hugepages; cp/ixcp.py needs Python 2 and posix_ipc |
| **Minimum toolchain** | Not documented. gcc builds the dataplane with -O3 -mno-red-zone -fno-pie; GCC 4.8 failed in DPDK's rte_memcpy.h when compiling i40e.c (issue #36; maintainer workaround: drop -no-pie from LDFLAGS and build with EXTRA_CFLAGS=-march=native). Control plane and ix-bench scripts are Python 2 only. Users report it running on Linux 3.16 and 4.4. |
| **Platforms** | x86-64 Linux host with Intel VT-x; Intel 82599/X520/X540 NICs via ixgbe (README). An i40e (XL710) driver was added in 2016 but users report it receives and never transmits (issue #31, open). IPv4 only (ip_tuple holds 32-bit addresses). |
| **Thread safety** | Per-thread design: each elastic thread owns its NIC queue, flow handles, memory pools and a __thread syscall batch array, so a handle is only used on the thread that owns it. The shared ARP table uses RCU. Elastic threads must not block; background threads may issue POSIX system calls, but the memcached port disabled its background maintenance threads with an 'XXX: hack' note that normal threads fail on newer kernels. |
| **Drop-in for the baseline** | partial — ixev mimics libevent but supports only edge-triggered, persistent events with no event timeouts (ixev.h FIXME); applications must be ported off sockets/libevent, relinked against libix.a and launched as `dp/ix -- ./app`, and the NIC is unbound from Linux for IX's exclusive use |

## Gotchas

- No receive flow control: if one connection holds 128 unconsumed receive segments (IXEV_RECV_DEPTH), ixev prints 'ixev: ran out of receive memory' and calls exit(-1); a single `nc < /dev/zero` flood took down the echoserver (issue #12). A full syscall batch array likewise exits with 'ran out of command space'.
- Zero-copy rules: received buffers are read-only and should be released quickly; send buffers must stay unmodified until the peer ACKs, or the wire payload is silently wrong. sendv returns bytes accepted by the TCP window, not bytes buffered, so partial sends are resumed on the 'sent' event.
- The TCP stack runs on the application's threads: a slow handler stalls every flow hashed to that core, and IX flags the app non-responsive after about 10ms in user mode. Outbound connections pick ephemeral ports so RSS returns replies to the same thread, so two threads cannot share a flow.
- Released artifacts differ from the paper: ix-bench's bench_memcached.py drives 2,720 connections from 16 threads (paper: 1,476), and the ported memcached disables its assoc-maintenance and slab-rebalance threads while the scripts pre-size the hash with hashpower=20. No IOMMU is used, so the dataplane is trusted with host-physical addresses; profiling needs `perf kvm --guest` because IX runs as a VT-x guest (issue #35).

## Known shortcomings

- Research dataplane OS: needs Dune/VT-x, GPL kernel modules and dedicated NICs; not a library. Code was released in 2016, two years after the OSDI '14 paper, and is abandoned since 2017-11. libdune has no licence file. No compiler versions stated.
- No receive flow control: one connection holding 128 unread segments makes the server exit (#12). The released benchmark differs from the paper (2,720 vs 1,476 connections; memcached maintenance threads disabled as a hack). DPDK pinned at 16.04, Python 2 scripts, Dune unlikely to build on recent kernels; IPv4 only, one instance per host, i40e transmit broken (#31).

## Caveats and trade-offs

OSDI 2014 peer-reviewed paper. The code was released in May 2016 (ix-project/ix and ix-project/ix-bench, whose scripts cover the OSDI'14 and SoCC'15 graphs), so the released code may differ from the 2014 prototype. The paper says outright that its Linux benchmarks use 'the libevent framework with the epoll system call' and that memcached is built on libevent. The win is over the Linux kernel TCP stack plus epoll, not over the event loop alone. IX's best config used 6 cores against Linux's 8. memcached was ported to IX's libix API, and the clients ran Linux. Running IX needs VT-x (Dune), DPDK, supported Intel NICs (the README lists 82599/X520/X540) and dedicated polling hardware threads and NIC queues. License: IX's own code is the MIT text under an 'IX Open Source License' header, so GitHub reports NOASSERTION. It statically links libdune from the ix-project/dune submodule, which has no license file, and needs GPL kernel modules (dune.ko MODULE_LICENSE GPL; pcidma GPL-2.0) plus DPDK. The paper says the dataplane is 41% derived from the DPDK ixgbe driver, 26% from lwIP and 15% from Dune. There have been no commits since 2017-11-06.

Research prototype OS requiring a custom kernel/dataplane split (built on the Dune hardware-virtualization mechanism); not a drop-in library and not portable to stock Linux without OS-level changes.

## Maintenance

Abandoned since 2017-11-06 (the maintainer still answered issues until 2021); IX's own code is MIT-style, but it needs the unlicensed Dune repo, kernel modules and DPDK 16.04 on old kernels, so treat it as a research artifact to study or reproduce, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B. The code is public after all: ix-project/ix (MIT text), plus ix-project/ix-bench, whose README says it holds the scripts that run the benchmarks and plot the graphs of the OSDI 2014 paper (bench_memcached.py). The paper is peer-reviewed, compares against Linux 3.16.1 with libevent+epoll and stock memcached-1.4.18, and names the server CPU (Xeon E5-2665 @ 2.4 GHz). It is not A because neither the paper nor the release states a compiler version. Flags appear only in build files (dp/Makefile gcc -O3; ix-bench Makefile gcc -O2), none for memcached, and the release dates from 2016, two years after the paper.
- **Verifier notes:** The record's 'no public code' premise is wrong. The orchestrator should set repo_url to https://github.com/ix-project/ix (C, not archived, not a fork, 136 stars), which is outside the allowed correction fields. The paper numbers (3.6x, 2.8x, &gt;2x tail, 10x/1.9x) were checked in the abstract, Sec 1, Sec 5.5 and Table 2. The license was read from the LICENSE text, and the libdune licensing gap is why usability is 'mixed'.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `license`, `usability`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-belay.pdf>
  - <https://github.com/ix-project/ix>
  - <https://github.com/ix-project/ix/blob/master/LICENSE>
  - <https://github.com/ix-project/ix/blob/master/README.md>
  - <https://github.com/ix-project/ix/blob/master/.gitmodules>
  - <https://github.com/ix-project/ix/blob/master/Makefile>
  - <https://github.com/ix-project/ix/blob/master/dp/Makefile>
  - <https://github.com/ix-project/ix/blob/master/dp/drivers/ixgbe.c>
  - <https://github.com/ix-project>
  - <https://github.com/ix-project/ix-bench>
  - <https://github.com/ix-project/ix-bench/blob/master/README.md>
  - <https://github.com/ix-project/ix-bench/blob/master/Makefile>
  - <https://github.com/ix-project/ix-bench/blob/master/bench_memcached.py>
  - <https://github.com/ix-project/memcached>
  - <https://github.com/ix-project/mutilate>
  - <https://github.com/ix-project/dune>
  - <https://github.com/ix-project/dune/blob/master/kern/core.c>
- **Sources the enricher read:**
  - <https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-belay.pdf>
  - <https://github.com/ix-project/ix>
  - <https://github.com/ix-project/ix/blob/master/README.md>
  - <https://github.com/ix-project/ix/blob/master/LICENSE>
  - <https://github.com/ix-project/ix/blob/master/.gitmodules>
  - <https://github.com/ix-project/ix/blob/master/Makefile>
  - <https://github.com/ix-project/ix/blob/master/dp/Makefile>
  - <https://github.com/ix-project/ix/blob/master/libix/Makefile>
  - <https://github.com/ix-project/ix/blob/master/libix/ixev.h>
  - <https://github.com/ix-project/ix/blob/master/libix/ixev.c>
  - <https://github.com/ix-project/ix/blob/master/libix/ix.h>
  - <https://github.com/ix-project/ix/blob/master/inc/ix/syscall.h>
  - <https://github.com/ix-project/ix/blob/master/ix.conf.sample>
  - <https://github.com/ix-project/ix/blob/master/apps/echoserver.c>
  - <https://github.com/ix-project/ix/blob/master/cp/ixcp.py>
  - <https://github.com/ix-project/ix/blob/master/dp/core/init.c>
  - <https://github.com/ix-project/ix/blob/master/dp/core/cpu.c>
  - <https://github.com/ix-project/ix/blob/master/dp/drivers/i40e.c>
  - <https://github.com/ix-project/ix/tree/master/deps>
  - <https://github.com/ix-project/ix/issues?q=is%3Aissue>
  - <https://github.com/ix-project/ix/pulls?q=is%3Apr>
  - <https://github.com/ix-project/ix/issues/2>
  - <https://github.com/ix-project/ix/issues/12>
  - <https://github.com/ix-project/ix/issues/24>
  - <https://github.com/ix-project/ix/issues/31>
  - <https://github.com/ix-project/ix/issues/34>
  - <https://github.com/ix-project/ix/issues/35>
  - <https://github.com/ix-project/ix/issues/36>
  - <https://github.com/ix-project/ix/issues/37>
  - <https://github.com/ix-project/ix/commits/master>
  - <https://github.com/ix-project/ix/wiki/Requirements>
  - <https://github.com/ix-project/ix-bench>
  - <https://github.com/ix-project/ix-bench/blob/master/README.md>
  - <https://github.com/ix-project/ix-bench/blob/master/bench_memcached.py>
  - <https://github.com/ix-project/ix-bench/blob/master/bench_common.py>
  - <https://github.com/ix-project/ix-bench/blob/master/Makefile>
  - <https://github.com/ix-project/memcached>
  - <https://github.com/ix-project/memcached/commits/ix>
  - <https://github.com/ix-project/memcached/compare/master...ix>
  - <https://github.com/ix-project/dune>
  - <https://github.com/ix-project/dune/blob/master/README>
  - <https://github.com/DPDK/dpdk/commit/b3b9719f18ee83773c6ed7adda300c5ac63c37e9>
  - <http://dpdk.org/git/dpdk>
  - <https://github.com/ix-project/mutilate>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `paper:ix-protected-dataplane-os`) · [data/wave5/enrich/raw/paper_ix_protected_dataplane_os.json](../../../data/wave5/enrich/raw/paper_ix_protected_dataplane_os.json) (enrichment confidence 0.8)

</details>
