# F-Stack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `BSD-2-Clause for F-Stack's main code, per the LICENSE file (GitHub reports 'Other'/NOASSERTION). Bundled components: DPDK BSD-3-Clause (kernel modules GPL-2.0), FreeBSD stack BSD-4-Clause, Nginx BSD-2-Clause, Redis BSD-3-Clause, libplebnet/libuinet BSD-2-Clause, inih BSD-3-Clause, Microthread framework GPL-2.0.` · 🟢 active

> DPDK kernel-bypass framework with a ported FreeBSD TCP/IP stack and epoll/kqueue-style API; beats kernel-stack epoll Nginx on RPS/CPS.

| | |
|---|---|
| **Beats** | epoll |
| **Claimed result** | README 'Nginx Testing Result' charts. Bandwidth values are the printed data labels; RPS/CPS values are approximate, read off the right axis of the chart images. CPS (Connection: close, 600-byte body, 1-20 cores): Nginx+F-Stack 5.82 Gbit/s (\~1.04M CPS) vs Nginx 'si' (kernel, IRQ smp_affinity spread, no reuseport) 0.47 Gbit/s (\~86k CPS) at 20 cores, \~12x (derived from page data). CPS_Reuseport (Connection: close, different test environment, 1-16 cores): F-Stack 5.78 Gbit/s (\~1.02M CPS) vs Nginx+reuseport 2.47 (\~0.44M) vs default Nginx 0.63 (\~0.11M) at 16 cores, \~2.3x vs reuseport (derived from page data). RPS (keep-alive, 600-byte body, 1-24 cores): F-Stack 26.96 Gbit/s (\~4.77M RPS) vs Nginx si 18.49 (\~3.27M) vs default Nginx 2.11 (\~0.38M) at 24 cores, \~1.46x vs the tuned kernel and \~12.8x vs the default config (derived from page data). Bandwidth (keep-alive, 3.7 KB body, 1-16 cores): F-Stack leads at low core counts (4.30 vs 2.90 Gbit/s at 1 core, 33.75 vs 23.28 at 8 cores, \~1.45x derived from page data), but both hit the \~37.1 Gbit/s 40GbE ceiling at 16 cores (parity). The README headline '10 million concurrent connections, 5 million RPS, 1 million CPS' under full NIC load: the 5M RPS and 1M CPS figures roughly match the charts, while the 10M-connection figure has no supporting chart. |
| **Workload** | Nginx serving a fixed body. CPS (Connection: close, 600-byte body), RPS (keep-alive, 600-byte body) and bandwidth (keep-alive, 3.7 KB body) on 1-24 physical cores. Kernel Nginx (Linux default config with all softirqs on core 0; 'si' = per-IRQ smp_affinity spread; 'Reuseport' = reuseport in nginx.conf) vs Nginx+F-Stack (DPDK kernel bypass plus a ported FreeBSD TCP/IP stack; body returned directly from nginx.conf). Intel XL710 40GbE NIC. |
| **Metric** | throughput |
| **Hardware** | Intel XL710 40GbE QSFP+ NIC, Intel Xeon E5-2670 v3 @ 2.30GHz (NUMA), 128GB RAM, CentOS 7.2, kernel 3.10.104-1-tlinux2 (the CPS_Reuseport chart was run in a different, unstated environment) |
| **Adoption** | 4,265 stars. Used in production at Tencent Cloud (DNSPod authoritative DNS, HttpDNS (D+), COS access module, CDN access module), per the README. |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/F-Stack/f-stack) · [benchmark](https://github.com/F-Stack/f-stack#nginx-testing-result) |

## Verdict

Tencent's README charts compare Nginx on the Linux 3.10 kernel stack (epoll) with Nginx+F-Stack on a Xeon E5-2670 v3 and an Intel XL710 40GbE NIC (CentOS 7.2; compiler and load generator not stated). F-Stack shows \~12x CPS/RPS over untuned kernel Nginx, but only \~1.46x RPS over IRQ-tuned Nginx (keep-alive, 24 cores) and \~2.3x CPS over reuseport Nginx (16 cores, different environment), and 3.7 KB-body bandwidth ties at 40GbE line rate. Values are read from chart images. A separate Photon wiki test (single thread, 25G NIC, 512 B messages) shows +20% ping-pong and +40% streaming over Linux 6.x kernel sockets.

## Use it when

- Dedicated front-end servers that open and close many short TCP connections (HTTP with Connection: close, L4/L7 proxies, TCP DNS), where kernel accept/teardown and softirq cost is the limit. The README shows \~2.3x CPS over reuseport-tuned kernel Nginx at 16 cores.
- Keep-alive serving of small requests over many connections spread across many cores: \~1.46x RPS over IRQ-affinity-tuned kernel Nginx at 24 cores on a 40GbE XL710.
- You already run Nginx or Redis and can switch to the bundled patched versions (Nginx 1.28.0, Redis 6.2.6) instead of rewriting code.
- You own the hardware: a NIC with a DPDK driver (Intel XL710/82599 and Mellanox ConnectX-5 appear in project reports, virtio in VMs) that you can give up entirely, plus hugepages and spare cores to pin at 100% busy-poll.
- Porting a C epoll/kqueue event loop where each core owning its own connections is a natural fit.

## Skip it when

- Single-connection or low-concurrency workloads. The maintainer calls a single TCP echo/stream F-Stack's worst case, and users measured it slower than Linux sockets (#774: 672 MB/s vs 1.88 GB/s for one-way 4 KB writes on the same host; #758: 350-400 vs 450-500 Mb/s in VMs).
- Bulk transfer that already saturates the NIC: with a 3.7 KB body both stacks reach \~37 Gbit/s on 40GbE at 16 cores, so there is no gain at line rate.
- Shared or general-purpose hosts, or containers without NIC passthrough. The data NIC disappears from Linux, so kernel tools and firewalls no longer see it, and without a separate management port even SSH needs the KNI/virtio exception path.
- Low-rate, latency-sensitive RPC on default settings: pkt_tx_delay=100 us and delayed ACK add latency to each round trip, and idle_sleep=0 burns a full core per lcore even when idle.
- macOS or Windows, or teams that cannot run as root, disable ASLR (required for multi-process mode) and operate DPDK in production.

## How it is fast

Kernel bypass: DPDK poll-mode drivers pull packets straight from NIC rings into hugepage mbufs on a busy-polling core, removing interrupts, syscalls, kernel copies and scheduler wakeups. Each lcore runs its own process (or thread with thread_mode=1) holding its own stack instance and RSS queue, so nothing is shared, and the port strips the FreeBSD stack's locks, kernel threads and scheduler. TX is batched (pkt_tx_delay holds up to 100 us while fewer than 32 packets are queued), and optional zero-copy send/receive (ff_zc_send/ff_zc_recv) skips socket-buffer copies.

## Compared with alternatives

Pick F-Stack over mTCP, IX or Arrakis when you want an actively maintained kernel-bypass TCP stack that is in production at Tencent Cloud, with the full FreeBSD TCP feature set and ready-made Nginx/Redis ports, rather than a paper-era research system. Pick Seastar instead if you are writing a new C++ service and accept its framework. If you must keep the Linux stack and a shared NIC, io_uring options (Asio's io_uring backend, monoio, Condy) give \~1.2-1.9x with far less operational burden.

## Integration

| | |
|---|---|
| **Form** | static lib (libfstack.a + ff_\*.h) plus bundled patched Nginx/Redis; optional shared lib libff_syscall.so for LD_PRELOAD |
| **Dependencies** | Bundled DPDK (24.11.6 on the dev branch), libnuma, OpenSSL, pkg-config &gt;= 0.28, meson/ninja and python3 pyelftools to build DPDK, igb_uio or vfio-pci driver, 2 MB hugepages, NIC with a DPDK poll-mode driver |
| **Minimum toolchain** | C built with GCC and GNU make (gmake on FreeBSD). Minimum GCC not documented: release notes fix builds on GCC 11.4 (Ubuntu 22.04), 12.2, 13.2 and 14.1, and CI builds in an Ubuntu 24 image. |
| **Platforms** | Linux and FreeBSD hosts; x86-64 primary, arm64 supported via lib/Makefile and freebsd/arm64; data-plane NIC must have a DPDK driver (bare metal, or virtio in VMs) |
| **Thread safety** | Not shared across instances. The FreeBSD stack's locks were removed, and each F-Stack process (or thread in thread_mode=1) owns its own stack, NIC queue and sockets, so call ff_\* only from that instance's ff_run loop. Threads made with ff_pthread_create panic if they touch per-CPU stack state. The LD_PRELOAD PIPELINE mode allows fds to be used across threads, at a performance cost. |
| **Drop-in for the baseline** | partial — the epoll calls are mirrored as ff_epoll_\* (built on kqueue), but you must rename calls, drive them from ff_run() and give the NIC to DPDK. The LD_PRELOAD adapter runs unmodified apps but needs a separate fstack process, and the project says it uses about twice the CPU. |

## Gotchas

- ff_epoll_wait ignores its timeout argument and always returns at once, because ff_run is the real loop. EPOLLET is emulated with kqueue EV_CLEAR, which the source says is not exactly the same. Sockets must be set non-blocking with ff_ioctl(FIONBIO), or ff_write can misbehave.
- Overload fails hard: when connections exhaust the mbuf pool, the whole stack becomes unresponsive, ff_\* tools included (#1076). An opt-in mbuf_low_watermark SYN-drop exists but is off by default, so cap kern.ipc.maxsockets to what the mbuf pool can hold.
- Defaults are tuned for high concurrency (pkt_tx_delay=100 us, net.inet.tcp.delayed_ack=1); maintainers tell single-connection users to lower both. The patched Nginx requires user root, sendfile off, use kqueue and worker_processes equal to the lcore count, and reload drops service for about 1 s unless graceful_reload=1.
- No ABI stability: a change to struct ff_config's layout made a helloworld built against the old lib segfault, so rebuild apps on every lib update. The docs lag the code: the README says FreeBSD 11.01/13.0, but dev ships a FreeBSD 15.0 stack (__FreeBSD_version 1500068) that measured 2-6% slower than 13.0 on Nginx short connections.

## Known shortcomings

- The \~12x headline is against untuned kernel Nginx; against the best-tuned kernel setup it is about 1.46x RPS and 2.3x CPS, and both hit the 40GbE limit at 3.7 KB. Numbers are read off the project's own charts; no compiler, flags, load generator or scripts published. The '10M concurrent connections' claim has no data, and the architecture doc's '25x vs kernel 200K RPS' contradicts the README. Needs DPDK and dedicated NICs; bundles BSD-4-Clause and GPL-2.0 parts.
- Worst case is single-connection and low-concurrency workloads: users measured it slower than Linux sockets (#774: 672 MB/s vs 1.88 GB/s; #758 in VMs). Exhausting the mbuf pool hangs the whole stack (#1076; safeguard off by default). ff_epoll_wait ignores its timeout and EPOLLET is emulated. Docs lag the code (FreeBSD 15.0 stack, DPDK 24.11); no ABI stability for ff_config.

## Caveats and trade-offs

Numbers exist only in chart images. Bandwidth data labels are readable, but RPS/CPS values are approximate reads off the chart axis. The \~12x ratios are against untuned or IRQ-only-tuned kernel Nginx. Against the best-tuned kernel config the gain is \~1.46x RPS (keep-alive, 24 cores) and \~2.3x CPS (vs reuseport, 16 cores), and 3.7 KB-body bandwidth reaches parity at 40GbE line rate. Compiler, flags, load generator and client setup are not stated, and no benchmark scripts are published. Hardware and kernel (E5-2670 v3, kernel 3.10) are 2016-era. The CPS_Reuseport chart ran in a different environment. The page does not say whether kernel Nginx also returned the body directly from nginx.conf. F-Stack is not a drop-in epoll replacement: it needs DPDK NIC takeover, hugepages and dedicated busy-polling cores, and the LD_PRELOAD adapter uses \~2x CPU (per adapter/syscall/README.md). The '10M concurrent connections' claim has no supporting data. docs/F-Stack_Architecture_Layer1_System_Overview.md claims '5M RPS vs kernel 200K RPS, 25x' without a source, and the README RPS chart contradicts it (kernel Nginx si \~3.27M RPS). BSD-4-Clause and GPL-2.0 components are bundled.

Requires DPDK + hugepages + dedicated NIC (kernel bypass), not a drop-in for arbitrary apps; Linux/FreeBSD only; adds operational complexity (core pinning, ASLR disabling); ported FreeBSD 11/13 TCP stack so feature/behavior parity with Linux netstack is not perfect

## Maintenance

Actively developed by Tencent Cloud: dev commits run through 2026-09-18, the last tagged release is v1.25 (2025-11), and dev is VERSION 2.0 on FreeBSD 15.0 and DPDK 24.11.6. The core is BSD-2-Clause, but the bundled BSD-4-Clause FreeBSD code and the GPL-2.0 kernel modules and micro-thread framework need license review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README charts (CPS.png, CPS_Reuseport.png, RPS.png, Bandwidth.png) compare Nginx on the Linux kernel stack (epoll) against Nginx+F-Stack, with hardware stated (Xeon E5-2670 v3, XL710 40GbE, CentOS 7.2, kernel 3.10.104). Compiler, flags, load generator and client setup are not stated and no benchmark scripts or configs for the kernel comparison are published, so it cannot be A; no peer-reviewed or independent suite was found, so C.
- **Verifier notes:** The charts could be read once downloaded (bandwidth data labels exact, RPS/CPS read off the axis), so claimed_speedup is filled in. The headline \~12x holds only against untuned or IRQ-tuned kernel Nginx; against tuned kernel configs the win is \~1.5-2.3x, with bandwidth parity at line rate. Supporting first-party data: adapter/syscall/README.md LD_PRELOAD charts, and the Photon wiki single-thread echo test (25G NIC, 512 B), which shows +20% ping-pong (1.23 vs 1.03 Gb/s) and +40% streaming (3.74 vs 2.60 Gb/s) vs Linux 6.x kernel sockets. last_commit is taken from default branch dev: release/2.0 has a commit on 2026-09-24, and no commit is dated 2026-09-25. Usability stays 'mixed' (BSD-2-Clause core plus non-OSI BSD-4-Clause and GPL-2.0 parts). No independent or peer-reviewed benchmark was searched for because the WebSearch budget is exhausted.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `license`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/F-Stack/f-stack#nginx-testing-result>
  - <https://github.com/F-Stack/f-stack>
  - <https://github.com/F-Stack/f-stack/blob/dev/README.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/LICENSE>
  - <https://github.com/F-Stack/f-stack/blob/dev/CPS.png>
  - <https://github.com/F-Stack/f-stack/blob/dev/CPS_Reuseport.png>
  - <https://github.com/F-Stack/f-stack/blob/dev/RPS.png>
  - <https://github.com/F-Stack/f-stack/blob/dev/Bandwidth.png>
  - <https://github.com/F-Stack/f-stack/tree/dev/doc>
  - <https://github.com/F-Stack/f-stack/tree/dev/docs>
  - <https://github.com/F-Stack/f-stack/blob/dev/docs/F-Stack_Architecture_Layer1_System_Overview.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/docs/freebsd_13_to_15_upgrade_spec/physical-machine-bench-report.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/docs/kernel_event_support_spec/10-perf-baseline-report.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Nginx_APP_Guide.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Release_Note.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/adapter/syscall/README.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/adapter/syscall/nginx-keep-alive.png>
  - <https://github.com/F-Stack/f-stack/blob/dev/adapter/syscall/nginx-close.png>
  - <https://github.com/F-Stack/f-stack/wiki>
  - <https://raw.githubusercontent.com/wiki/F-Stack/f-stack/Home.md>
  - <https://raw.githubusercontent.com/wiki/F-Stack/f-stack/%5BPhoton---F%E2%80%90Stack%5D-Coroutine-made-DPDK-dev-easy.md>
  - <https://raw.githubusercontent.com/wiki/F-Stack/f-stack/F-Stack-Send-Zero-Copy-Introduction---Translate-by-@Xlight5.md>
  - <http://www.f-stack.org/>
- **Sources the enricher read:**
  - <https://github.com/F-Stack/f-stack>
  - <https://github.com/F-Stack/f-stack#nginx-testing-result>
  - <https://github.com/F-Stack/f-stack/blob/dev/lib/ff_api.h>
  - <https://github.com/F-Stack/f-stack/blob/dev/lib/ff_epoll.c>
  - <https://github.com/F-Stack/f-stack/blob/dev/lib/Makefile>
  - <https://github.com/F-Stack/f-stack/blob/dev/config.ini>
  - <https://github.com/F-Stack/f-stack/blob/dev/VERSION>
  - <https://github.com/F-Stack/f-stack/blob/dev/dpdk/VERSION>
  - <https://github.com/F-Stack/f-stack/blob/dev/freebsd/sys/param.h>
  - <https://github.com/F-Stack/f-stack/blob/dev/example/main_epoll.c>
  - <https://github.com/F-Stack/f-stack/blob/dev/.github/workflows/ci.yml>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_API_Reference.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Development_Guide.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Build_Guide.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Roadmap.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Release_Note.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Nginx_APP_Guide.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/adapter/README.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/adapter/syscall/README.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/docs/freebsd_13_to_15_upgrade_spec/physical-machine-bench-report.md>
  - <https://github.com/F-Stack/f-stack/blob/dev/docs/kernel_event_support_spec/10-perf-baseline-report.md>
  - <https://github.com/F-Stack/f-stack/releases>
  - <https://github.com/F-Stack/f-stack/issues/758>
  - <https://github.com/F-Stack/f-stack/issues/594>
  - <https://github.com/F-Stack/f-stack/issues/774>
  - <https://github.com/F-Stack/f-stack/issues/1076>
  - <https://github.com/F-Stack/f-stack/issues/545>
  - <https://raw.githubusercontent.com/wiki/F-Stack/f-stack/Home.md>
  - <https://raw.githubusercontent.com/wiki/F-Stack/f-stack/%5BPhoton---F%E2%80%90Stack%5D-Coroutine-made-DPDK-dev-easy.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/f-stack/f-stack`) · [data/wave5/enrich/raw/github_com_f_stack_f_stack.json](../../../data/wave5/enrich/raw/github_com_f_stack_f_stack.json) (enrichment confidence 0.6)

</details>
