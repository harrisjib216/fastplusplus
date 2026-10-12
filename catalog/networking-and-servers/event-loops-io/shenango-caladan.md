# Caladan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Interference-aware core scheduler and kernel-bypass runtime; memcached 99.9% latency 52 us vs 580 ms under Parties\* during GC.

| | |
|---|---|
| **Beats** | Parties (authors' reimplementation, 'Parties\*', because the original source was unavailable); also compared with Linux (kernel TCP, BE task at SCHED_IDLE) and Shenango |
| **Claimed result** | Vs Parties\* (memcached + swaptions-GC): 99.9% latency 11,000x lower during GC cycles ('reducing tail latency from 580 ms to 52 us'), and Parties\* BE throughput averaged 5% less than Caladan's. Vs Linux and Shenango (constant stream-DRAM interference, Fig. 4): their tail latency rose 'up to 235x and 6x higher than without interference' and Shenango's throughput fell 75%. Caladan (and Parties\*) kept similar tail latency with and without interference and achieved 'much higher throughput than Linux and Shenango' (graph only, no exact numbers). KSCHED vs a variant using Linux syscalls (sched_setaffinity/tgkill/eventfd): the Linux variant needs 43x more scheduling work and 5x the scheduling latency when moving 22 tasks, and bottlenecks at \~285,000 core reallocations/s vs Caladan's peak of 560,000 (at 0.65 MRPS). |
| **Workload** | memcached 1.5.6 (Facebook USR mix, \~1 us service time) at 800,000 requests/s over TCP, colocated with swaptions-GC (a PARSEC job using the Boehm GC); 99.9th-percentile latency measured over 20 ms windows during a 120 s run. A second test colocated memcached with the stream-DRAM bandwidth antagonist and compared against Linux and Shenango (Fig. 4). |
| **Metric** | latency |
| **Hardware** | Server with two 12-core (24-hyperthread) Intel Xeon Broadwell CPUs (exact model not stated) and 64 GB RAM, running Ubuntu 18.04 with kernel 5.2.0 modified for faster multicast IPIs (Linux baseline on kernel 5.4.0). Only socket 0 used; 40 Gb/s Mellanox ConnectX-5 NIC; 280 GB Intel Optane NVMe. Clients were quad-core machines with 10 Gb/s ConnectX-3 NICs behind a Mellanox SX1024 switch. TurboBoost, C-states, frequency scaling and THP were off, as were the Meltdown/MDS mitigations. Caladan ran with 22 guaranteed LC cores plus one physical core for the scheduler. |
| **Compiler and flags** | Not stated in the paper. The current repo build (build/shared.mk) uses CC ?= gcc (CONFIG_CLANG=y switches to clang), -std=gnu11 for C and -std=gnu++20 for C++, and -O3 -DNDEBUG; CONFIG_OPTIMIZE=y adds -march=native -flto=auto -ffat-lto-objects -ffast-math. These are today's flags, not the 2020 evaluation build. |
| **Adoption** | 200 stars, 78 forks. Per the paper, it is derived from Shenango's open-source release (a new scheduler plus the ksched module). |
| **Last commit** | 2026-05-10 |
| **Links** | [repository](https://github.com/shenango/caladan) · [benchmark](https://www.usenix.org/system/files/osdi20-fried.pdf) |

## Verdict

OSDI '20 paper, run on one socket of a dual 12-core Xeon Broadwell server (exact model not given) with a 40 GbE ConnectX-5 and a kernel 5.2 patched for faster multicast IPIs, with security mitigations off and no compiler stated. With memcached 1.5.6 (USR mix, 800k req/s) next to a Boehm-GC PARSEC swaptions job, Caladan kept 99.9th-percentile latency (20 ms windows) near 52 us through GC cycles, while the authors' own Parties reimplementation (Parties\*, given the same kernel-bypass runtime and hyperthreads) peaked at 580 ms (11,000x) and got 5% less batch throughput. Linux (kernel TCP on 5.4, BE at SCHED_IDLE) and Shenango appear only in a graph, where stream-DRAM interference raised each one's tail latency 235x and 6x over its own no-interference run. A microbenchmark comparing ksched with Linux syscalls showed 43x less scheduler work, 5x lower latency when moving 22 tasks, and 560k vs \~285k core reallocations/s.

## Use it when

- A single-socket x86-64 server that colocates microsecond-scale LC services (memcached, RPC, NVMe block storage) with batch jobs whose memory-bandwidth or cache use changes in phases (garbage collection, video encoding, clustering), where 99.9th-percentile latency must stay in the tens of microseconds and batch work should still use the idle cycles.
- Several LC and BE tasks on one box with hyperthreads left on. The paper ran 3 LC and 2 BE apps together at up to 230,000 core reallocations/s, with per-task knobs (runtime_qdelay_us, runtime_ht_punish_us, guaranteed vs burstable kthreads).
- You control the whole machine and can give iokerneld a physical core, load a kernel module as root, reserve hugepages, and use an NVIDIA/Mellanox ConnectX-4 or newer NIC with directpath.
- New C, C++ (gnu++20 bindings) or Rust-nightly services written as blocking green threads, or anything now on Shenango: Caladan is its maintained successor with the same runtime model.
- Research on microsecond-scale scheduling: the IOKernel has pluggable policies (ias, simple, experimental numa), and test.sh runs it on a DPDK tap vdev with no real NIC.

## Skip it when

- You need Linux sockets, epoll/io_uring compatibility, TLS or HTTP, or want to keep an existing event-loop server unchanged. Nothing is drop-in: LC services must be ported to its green-thread API, and processes outside the runtime cannot be throttled.
- Multi-socket or multi-tenant hosts. It cannot manage interference across NUMA nodes (the numa policy is described as incomplete and experimental), and sharing hyperthread siblings between tasks does nothing against transient-execution attacks; the paper also ran with Meltdown and MDS mitigations off.
- WAN or lossy networks. The TCP stack has window scaling and fast retransmit, but I found no congestion-window or SACK code, and the retransmit timeout is fixed at 300 ms with a FIXME comment.
- Hardware off the tested path: non-x86 CPUs, ConnectX-3 (dropped; issue #20, 2024), hyperthreading disabled in BIOS (open issue #22), or servers where PCM cannot reach the uncore counters. Non-directpath NICs (ixgbe, i40e and other DPDK PMDs) run, but the maintainers treat that as a testing setup, not a benchmarking one.
- LC services that multiplex many connections per thread and cannot be restructured. Without a green thread per connection or per request, extra cores do not help, so the allocator cannot absorb load or interference.

## How it is fast

Parties and Heracles partition hardware (Intel CAT/MBA) and adjust every \~500 ms or more. Caladan reallocates whole cores based on signals it reads every 10 us: the queueing delay of the oldest item in each core's runqueue, NIC RX, storage and timer queues (all in shared memory); global DRAM bandwidth from uncore counters, attributed to tasks by sampling per-core LLC misses; and how long each hyperthread has been on its current request. Three controllers act on these signals. The top-level allocator adds a core to any task over its queueing-delay threshold, the bandwidth controller takes one core per 10 us from the BE task with the most LLC misses while bandwidth is above a limit, and the hyperthread controller idles (mwait) the sibling of an LC request that runs past its threshold, a policy generalized from Elfen scheduling. KSCHED keeps these moves cheap: commands pass through per-core 64-byte shared-memory slots, one multicast IPI kicks many cores, calls are asynchronous, and signal delivery and affinity changes run on the target core. Runtime cores also send and receive their own packets (libibverbs/directpath), so the scheduler core does not forward traffic the way Shenango's did.

## Compared with alternatives

Pick it over Shenango for any new work: same runtime model, still maintained, directpath removes the IOKernel packet bottleneck, and it adds memory-bandwidth and hyperthread interference control. Pick it over IX, mTCP, F-Stack or Demikernel when the goal is colocating microsecond-scale services with batch jobs on shared cores rather than peak throughput for one app on dedicated cores; if you only need a faster event loop on stock Linux sockets, the io_uring siblings (monoio, Condy) need no dedicated core, kernel module or porting.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | git submodules built by `make submodules`: DPDK 25.03 and rdma-core (both patched), Intel PCM (patched), and SPDK (only with CONFIG_SPDK=y). apt packages: libnl-3/libnl-route-3, libnuma, uuid, libssl, libaio, libcunit1, libclang, libncurses, meson, pyelftools and libarchive. Also the ksched kernel module (GPL; fake_idle.ko too when no cpuidle driver is loaded), 2 MB hugepages, the msr module, and the iokerneld daemon run as root. Rust nightly (bindgen 0.69) for loadgen and the Rust bindings. Mellanox OFED 4.6+ and DEVX-capable NIC firmware for directpath. |
| **Minimum toolchain** | GCC by default, or clang with CONFIG_CLANG=y; C is -std=gnu11 and the C++ bindings need -std=gnu++20. The default build adds -muintr, -mxsavec and -mfsgsbase (set CONFIG_NO_UINTR=y for compilers without UINTR), and the default CONFIG_OPTIMIZE=y adds -march=native -flto=auto -ffast-math. No minimum compiler version is documented. Building ksched needs kernel headers. Tested on Ubuntu 18.04 (kernel 5.2) through 24.04 (kernel 6.8). |
| **Platforms** | x86-64 Linux only (kernel 5.0+ for directpath). NICs: its own mlx5 driver for ConnectX-4 and newer is fastest; DPDK PMDs ixgbe, i40e, ice, bnxt, mana (Azure VMs are auto-detected), failsafe, mlx5 and tap are slower; no mlx4/ConnectX-3. It manages one NUMA node, with compile-time limits of 256 CPUs and 4 NUMA nodes. Memory-bandwidth control reads uncore counters through PCM. |
| **Thread safety** | Built for multi-core use: green threads migrate between kthreads by work stealing, and the IOKernel can preempt kthreads (signals delivered through ksched, or Intel user interrupts on CPUs with UINTR). Synchronize with the runtime's mutex, rwmutex, condvar, waitgroup, barrier, spinlock and RCU primitives, and wrap per-kthread state in preempt_disable/preempt_enable. Other thread-safety rules are not documented. |
| **Drop-in for the baseline** | partial — Parties and Linux scheduling manage unmodified processes, but Caladan manages only programs linked against its runtime. pthread batch jobs run unmodified through libshim.a (-Wl,--wrap=main, with no static pthread mutex initializers). LC network services must be ported to its tcp_\*/udp_\* green-thread API and expose concurrency (a thread per connection or per request), as the authors did for memcached. Programs not using the runtime must run on unmanaged cores. |

## Gotchas

- The README says plain `sudo ./iokerneld` runs Shenango's default scheduler and `iokerneld ias` turns on interference control, but current iokernel/main.c picks ias when no policy is given; `simple` is the policy without interference control. The bandwidth controller has a hard-coded 25,000 MB/s default limit (IAS_BW_LIMIT, the paper's value, 70-80% of its test machine's capacity; override it with `bwlimit`). It also needs PCM uncore access, and users who hit 'Can not access server uncore PCI configuration space' (#21) or a resctrl conflict (#35) fell back to `nobw`, which turns off the protection against memory-bandwidth hogs.
- Without directpath, the single IOKernel core both forwards packets and runs the controllers. A user on 82599ES NICs could not reproduce the interference isolation until moving to mlx5 with directpath (#35). Each directpath runtime must run as root with a unique IP.
- The default CONFIG_OPTIMIZE=y builds with -march=native and -ffast-math, so binaries only run on the build machine's CPU type. Apps must be rebuilt whenever Caladan changes: a mismatched memcached build dropped every packet, and old host_mac/static_arp config lines break TCP on current versions (#30).
- Setup is heavy: setup_machine.sh reserves 5,192 2 MB hugepages (\~10 GB) on every NUMA node, sets THP to madvise and makes /dev/ksched world-writable, and each green thread reserves a 512 KB stack plus a 512 KB guard. The paper's multicast-IPI speedup came from a patched 5.2 kernel, but today's ksched uses the stock smp_call_function_many, which the paper says costs more under memory-bandwidth interference, so its KSCHED numbers may not carry over to stock kernels.

## Known shortcomings

- README says plain iokerneld runs Shenango's default scheduler, but main.c now picks the ias (Caladan) policy. The memory-bandwidth limit is hard-coded at 25,000 MB/s (tuned to the paper's machine); the controller needs PCM uncore access, and users hitting PCI-config (#21) or resctrl (#35) errors fell back to nobw, losing bandwidth-interference protection. Directpath (mlx5) is effectively required; without it one IOKernel core forwards all packets and isolation did not reproduce on 82599ES (#35). The paper's IPI speedup came from a patched 5.2 kernel; stock smp_call_function_many is costlier under interference. TCP has no congestion window or SACK and a fixed 300 ms RTO (FIXME): not for WAN or lossy links. x86-64 Linux, one NUMA node (numa policy experimental); ConnectX-3 dropped (#20); hyperthreading off asserts (#22); shared hyperthreads give no transient-execution protection (paper ran with Meltdown/MDS mitigations off). Default build uses -march=native -ffast-math and -muintr; apps must be rebuilt on every Caladan change (#30). setup_machine.sh reserves \~10 GB hugepages per node and makes /dev/ksched world-writable; 512 KB stack + 512 KB guard per green thread; dedicated scheduler core and root daemon; ksched is GPL. LC services must be ported; caladan-all artifact fails to compile (#30).

## Caveats and trade-offs

The 11,000x figure is against the authors' own reimplementation of Parties, which they gave kernel-bypass networking and hyperthreads (hence 'Parties\*'). It is a peak-window value taken only during GC cycles (580 ms vs 52 us), not a steady-state average; the separate 500,000x figure is convergence speed compared with Parties' published typical speed. The Linux and Shenango comparison exists only as a graph (Fig. 4): the 235x and 6x ratios compare those systems with and without interference, not with Caladan, and Caladan's throughput lead over Linux comes mostly from kernel-bypass networking. The Linux baseline also ran a different kernel (5.4.0 vs modified 5.2.0). Neither Parties\* nor Linux is a listed event-loops-io baseline (libuv/libevent/epoll/io_uring). IX and Arachne appear in related work only and were not measured. No compiler or flags are given, and the CPU is named only as 'Xeon Broadwell'; security mitigations were disabled. The artifact repo (github.com/shenango/caladan-all, which has no license file) has a paper_experiments.py that drives only Caladan configurations (figure 7, 8, 9b ksched-vs-pinned, 9c and the memcached timeseries). Its helper code has partial linux/shenango configurations and a memcached-linux submodule, but there is no driver for the Parties\*, Linux/Shenango (Fig. 4) or Linux-syscall-variant comparisons. These are 2020 numbers, and the code has changed a lot since then (current kernels 5.15/6.8, directpath, DPDK PMDs).

Apps must link Caladan's own runtime (green threads, its own TCP/UDP stack) and are not Linux-compatible. A pthread shim runs PARSEC-style batch jobs unmodified, but network services have to be ported, and LC tasks must expose concurrency with a thread per connection or per request (the authors changed memcached this way). It takes one dedicated scheduler core (iokerneld, run as root), the ksched kernel module and hugepages. It runs best with its own mlx5 driver on ConnectX-4 or newer; DPDK PMDs work but are slower, and directpath needs Mellanox OFED, DEVX firmware and root. It is x86-64 Linux only, cannot manage interference across NUMA nodes, and its hyperthread co-scheduling does nothing about transient-execution attacks between sibling hyperthreads.

## Maintenance

Actively maintained by the MIT authors (last main-branch commit 2026-05-10, maintainers reply to most issues, tested through Ubuntu 24.04/kernel 6.8) and Apache-2.0 with a GPL kernel module; it is a platform you deploy on a dedicated machine rather than a library to vendor, and the paper's artifact repo (caladan-all) has fallen behind the main repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed OSDI '20 paper (osdi20-fried.pdf) states every claimed figure in the text: 11,000x and 580 ms vs 52 us against Parties\*, 235x/6x/75% for Linux/Shenango, and 43x, 5x and 560k vs 285k for KSCHED vs Linux syscalls. It is not A because neither the paper nor the artifact gives a CPU model ('Xeon Broadwell') or compiler/flags, and the artifact has no driver for the baseline runs. I did not apply the &gt;50x cap: the 11,000x is a GC-window tail-latency result explained by Parties' 500 ms adjustment interval, not a compiler-sensitive microbenchmark.
- **Verifier notes:** All numbers and hardware details match the OSDI '20 PDF. Metadata checked via GitHub GraphQL (REST was rate-limited): Apache-2.0, 200 stars, 78 forks, not a fork or archived, last commit 2026-05-10, so active. I set baseline_in_list to false to match wave 5 precedent (Shenango, Demikernel and FlexTOE with Linux-kernel baselines are false).
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/osdi20-fried.pdf>
  - <https://github.com/shenango/caladan>
  - <https://github.com/shenango/caladan-all>
  - <https://raw.githubusercontent.com/shenango/caladan/main/build/shared.mk>
  - <https://raw.githubusercontent.com/shenango/caladan/main/README.md>
  - <https://raw.githubusercontent.com/shenango/caladan-all/master/README.md>
  - <https://raw.githubusercontent.com/shenango/caladan-all/master/paper_experiments.py>
  - <https://raw.githubusercontent.com/shenango/caladan-all/main/caladan_common.py>
  - <https://raw.githubusercontent.com/shenango/caladan-all/main/experiment.py>
  - <https://raw.githubusercontent.com/shenango/caladan-all/main/globals.py>
- **Sources the enricher read:**
  - <https://github.com/shenango/caladan>
  - <https://github.com/shenango/caladan/blob/main/README.md>
  - <https://github.com/shenango/caladan/blob/main/build/shared.mk>
  - <https://github.com/shenango/caladan/blob/main/build/config>
  - <https://github.com/shenango/caladan/blob/main/build/init_submodules.sh>
  - <https://github.com/shenango/caladan/blob/main/Makefile>
  - <https://github.com/shenango/caladan/blob/main/.gitmodules>
  - <https://github.com/shenango/caladan/blob/main/CONTRIBUTING.md>
  - <https://github.com/shenango/caladan/blob/main/sample.config>
  - <https://github.com/shenango/caladan/blob/main/server.config>
  - <https://github.com/shenango/caladan/blob/main/victim.config>
  - <https://github.com/shenango/caladan/blob/main/antagonist.config>
  - <https://github.com/shenango/caladan/blob/main/test.sh>
  - <https://github.com/shenango/caladan/blob/main/scripts/setup_machine.sh>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/runtime.h>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/thread.h>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/tcp.h>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/sync.h>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/preempt.h>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/smalloc.h>
  - <https://github.com/shenango/caladan/blob/main/inc/runtime/storage.h>
  - <https://github.com/shenango/caladan/blob/main/inc/base/limits.h>
  - <https://github.com/shenango/caladan/blob/main/inc/iokernel/control.h>
  - <https://github.com/shenango/caladan/blob/main/runtime/cfg.c>
  - <https://github.com/shenango/caladan/blob/main/runtime/sched.c>
  - <https://github.com/shenango/caladan/blob/main/runtime/preempt.c>
  - <https://github.com/shenango/caladan/blob/main/runtime/defs.h>
  - <https://github.com/shenango/caladan/blob/main/runtime/net/tcp.h>
  - <https://github.com/shenango/caladan/blob/main/runtime/net/tcp_in.c>
  - <https://github.com/shenango/caladan/blob/main/runtime/net/tcp_out.c>
  - <https://github.com/shenango/caladan/blob/main/iokernel/main.c>
  - <https://github.com/shenango/caladan/blob/main/iokernel/defs.h>
  - <https://github.com/shenango/caladan/blob/main/iokernel/ias.h>
  - <https://github.com/shenango/caladan/blob/main/iokernel/ias.c>
  - <https://github.com/shenango/caladan/blob/main/ksched/ksched_main.c>
  - <https://github.com/shenango/caladan/blob/main/ksched/uintr.c>
  - <https://github.com/shenango/caladan/blob/main/ksched/fake_idle.c>
  - <https://github.com/shenango/caladan/blob/main/ksched/Kbuild>
  - <https://github.com/shenango/caladan/blob/main/ksched/Makefile>
  - <https://github.com/shenango/caladan/blob/main/shim/README>
  - <https://github.com/shenango/caladan/blob/main/shim/Makefile>
  - <https://github.com/shenango/caladan/blob/main/bindings/cc/Makefile>
  - <https://github.com/shenango/caladan/blob/main/bindings/cc/thread.h>
  - <https://github.com/shenango/caladan/blob/main/bindings/cc/net.h>
  - <https://github.com/shenango/caladan/blob/main/bindings/rust/Cargo.toml>
  - <https://github.com/shenango/caladan/blob/main/bindings/rust/rust-toolchain.toml>
  - <https://github.com/shenango/caladan/blob/main/breakwater/README.md>
  - <https://github.com/shenango/caladan/commits/main>
  - <https://github.com/shenango/caladan/issues>
  - <https://github.com/shenango/caladan/pulls>
  - <https://github.com/shenango/caladan/issues/13>
  - <https://github.com/shenango/caladan/issues/15>
  - <https://github.com/shenango/caladan/issues/17>
  - <https://github.com/shenango/caladan/issues/20>
  - <https://github.com/shenango/caladan/issues/21>
  - <https://github.com/shenango/caladan/issues/22>
  - <https://github.com/shenango/caladan/issues/30>
  - <https://github.com/shenango/caladan/issues/31>
  - <https://github.com/shenango/caladan/issues/33>
  - <https://github.com/shenango/caladan/issues/35>
  - <https://github.com/shenango/caladan/issues/38>
  - <https://www.usenix.org/system/files/osdi20-fried.pdf>
  - <https://github.com/shenango/caladan-all>
  - <https://raw.githubusercontent.com/shenango/caladan-all/master/README.md>
  - <https://github.com/DPDK/dpdk/commit/fa3aca8a525decfd12bd5fa01ebc98789d5f7278>
  - <https://hn.algolia.com/api/v1/search?query=%22Caladan%22%20interference&typoTolerance=false>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/shenango/caladan`) · [data/wave5/enrich/raw/github_com_shenango_caladan.json](../../../data/wave5/enrich/raw/github_com_shenango_caladan.json) (enrichment confidence 0.85)

</details>
