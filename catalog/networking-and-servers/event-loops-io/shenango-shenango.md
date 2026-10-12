# Shenango

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Kernel-bypass runtime reallocating cores every 5 us; ZygOS-level tail latency, 6.3x Linux DNS throughput, idle cores freed for batch jobs.

| | |
|---|---|
| **Beats** | ZygOS (a state-of-the-art kernel-bypass network stack) and standard Linux kernel networking |
| **Claimed result** | NSDI'19 paper: memcached (USR workload): Shenango handles over 5 million requests/s with 37 us median and 93 us 99.9th-percentile latency, keeping 99.9th-percentile latency below 100 us at 'one million more than ZygOS' (ZygOS keeps similar response times only up to \~4 million requests/s). Linux memcached reaches about 800,000 requests/s before 99th-percentile latency spikes (no batch work). With batch work, Linux's 99.9th-percentile latency at 0.4M requests/s goes from 83 us to over 2 ms. gdnsd DNS over UDP: Linux up to 900,000 requests/s (41 us median) vs Shenango 5.7 million requests/s, 'a 6.33x improvement' (36 us median, 73 us 99.9th percentile). Thread microbenchmarks (Table 2): spawn-join 148 ns vs 12,996 ns with Linux pthreads; condvar ping-pong 100 ns vs 1,900 ns. Per the abstract, unlike ZygOS, Shenango can linearly trade latency-sensitive throughput for batch-processing throughput. |
| **Workload** | memcached 1.5.6 USR workload (99.8% GET / 0.2% SET) over TCP; Rust spin-server with constant/exponential/bimodal service times (10 us mean); gdnsd 2.4.0 DNS over UDP. Each runs alongside PARSEC swaptions batch work, with 1,200 persistent connections from 6 client machines and all systems limited to 16 hyperthreads. Also load-burst tests (100k to 5M requests/s) and thread-operation microbenchmarks vs pthreads, Go and Arachne. Core reallocation every 5 us. |
| **Metric** | other |
| **Hardware** | Dual-socket server with 12-core Intel Xeon E5-2650v4 @ 2.20 GHz (first socket only, hyper-threads on, TurboBoost, C-states and frequency scaling disabled), 64 GB RAM, 10 Gb/s Intel 82599ES NIC; Ubuntu 18.04, kernel 4.15.0 (ZygOS on Ubuntu 16.04, kernel 4.11.0); load from six quad-core machines through a Mellanox SX1024 switch with ConnectX-3 Pro NICs |
| **Compiler and flags** | Not stated in the paper. Repo Makefiles: gcc (runtime/IOKernel) and g++ (apps/bench) with -O3 -DNDEBUG -mssse3 (non-DEBUG build); Rust apps built with cargo --release on nightly. No compiler versions given. |
| **Adoption** | 151 stars; NSDI'19 paper |
| **Last commit** | 2024-11-05 |
| **Links** | [repository](https://github.com/shenango/shenango) · [benchmark](https://www.usenix.org/system/files/nsdi19-ousterhout.pdf) |

## Verdict

NSDI'19 paper, on one socket of a 12-core Xeon E5-2650v4 (all systems capped at 16 hyperthreads, 2 of them for the IOKernel) with an Intel 82599ES 10 GbE NIC, Ubuntu 18.04/kernel 4.15 and no compiler stated: memcached 1.5.6 (USR workload) next to PARSEC swaptions served over 5M requests/s at 37 us median and 93 us 99.9th percentile, about 1M requests/s more than ZygOS under the same latency bound, while leaving idle cycles to the batch job (ZygOS left none). Linux reached only \~0.8M requests/s even without batch work (and exceeded 2 ms 99.9th percentile at 0.4M with batch work), and ported gdnsd did 5.7M vs 0.9M UDP requests/s on Linux (6.33x).

## Use it when

- A single-socket x86-64 server that runs a latency-critical request/response service (1-10 us service times, memcached- or RPC-like) next to batch work, where you need 99.9th-percentile latency under \~100 us and want idle cores to go to the batch job.
- Load that jumps within microseconds (the paper tests 100k to 5M requests/s steps) where static kernel-bypass provisioning such as ZygOS or IX would have to keep all cores spinning for peak load.
- High-rate small UDP request/response services on one 10 GbE port (gdnsd port: 5.7M vs 0.9M requests/s on Linux).
- Research or reproduction of the NSDI'19 results, or as a readable reference for microsecond-scale core allocation (the whole congestion check and grant loop is about 80 lines in iokernel/cores.c).
- You can give a full physical core (2 hyperthreads) to iokerneld, run it as root, and bind the NIC to DPDK.

## Skip it when

- Any new deployment: the maintainers mark it unmaintained and point to Caladan, which adds directpath (IOKernel off the datapath), TCP window scaling, user-interrupt time slicing and interference mitigations.
- WAN, lossy or high bandwidth-delay paths: the from-scratch TCP stack has flow control and fast retransmit but no congestion control and no window scaling.
- Peak throughput at very short service times (&lt;2 us): the single IOKernel core caps out around 6.5M packets/s and becomes the bottleneck; ZygOS reaches higher peak memcached throughput (at worse latency).
- Multi-socket/NUMA use, VMs, non-x86 CPUs, hosts without hyperthreading, or NICs other than the tested Intel 82599ES and Mellanox ConnectX-3 Pro (ConnectX-5 patches exist): the IOKernel only manages cores on package 0 and panics if hyperthreads are off unless built with CORES_NOHT; VM support is an unanswered issue.
- You need HTTP, TLS or BSD-socket compatibility: none is provided, and existing servers must be rewritten against tcp_\*/udp_\* calls.

## How it is fast

One busy-polling IOKernel core runs a congestion-detection check every 5 us: if any uthread or packet stays in a kthread's ring-buffer queue across two consecutive checks (current head vs previous tail, read from one shared cache line per kthread), the app gets one more core, and kthreads that find no work after local, hyperthread-sibling, random and all-kthread work stealing park and hand the core back. Cores are granted with eventfd wakeups plus sched_setaffinity and taken back with tgkill(SIGUSR1); a reallocation completes in 5.9 us, and the paper contrasts its 5 us balancing interval with 4 ms for Linux and 50 ms for Arachne. Inside the app, per-kthread runqueues with lock-free local wakeups, preallocated stacks, minimal register saves on cooperative yield, and stealing of packet/TCP processing across cores (dropping flow-consistent hashing, unlike ZygOS) keep scheduling cheap. Payloads are copied instead of zero-copy so Intel DDIO keeps packet buffers inside its LLC share.

## Compared with alternatives

Pick Shenango over Demikernel or eRPC only when the goal is CPU efficiency, meaning microsecond-scale core reallocation among colocated apps behind a blocking-thread API, rather than the lowest per-request latency or RPC rate; for HTTP serving use Lwan or H2O, since Shenango has no HTTP layer. In practice, prefer its maintained successor Caladan.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | DPDK 19.11 as a git submodule with patched ixgbe/mlx4/mlx5 drivers (the paper used 18.11), libnuma, libdl, pthreads, 2 MB hugepages and System V shared memory (scripts/setup_machine.sh), a root-run iokerneld daemon; Mellanox OFED for Mellanox NICs; Rust bindings need bindgen 0.32 (clang) and a nightly toolchain |
| **Minimum toolchain** | GCC with -std=gnu11 (runtime, IOKernel) and -std=gnu++11 (C++ bindings), -mssse3, -O3; no GCC version documented. Rust bindings use #![feature(llvm_asm)], which rustc nightly removed in January 2022, so a 2021 nightly is needed (issue #10 reports nightly-2021-06-06 works). Tested on Ubuntu 18.04, kernel 4.15. |
| **Platforms** | x86-64 Linux only; single socket (package 0); hyperthreading required by default; Intel 82599ES (ixgbe) or Mellanox ConnectX-3 Pro/ConnectX-5 via DPDK |
| **Thread safety** | Built for multi-core use: uthreads migrate between kthreads via work stealing and the runtime supplies mutex, condvar and RCU. Blocking Linux syscalls are discouraged, and code must wrap thread-local accesses (including glibc malloc/free) in preempt_disable/preempt_enable because gcc caches TLS addresses across preemption; smalloc/sfree are the runtime's allocator. |
| **Drop-in for the baseline** | partial — the pthread shim (link libshim.a with -Wl,--wrap=main) runs unmodified pthread batch programs, but network services must be ported from Linux sockets or ZygOS's event API to Shenango's blocking tcp_\*/udp_\* calls and started under runtime_init with a config file |

## Gotchas

- TCP interop is limited: no window scaling (an mTCP client that assumed window scaling stalled because Shenango read its receive window as tiny, issue #6), no congestion control, and reader wakeups depend on the peer setting PSH or FIN.
- Packet stealing and core changes reorder packets: under 0.07% arrive out of order with 1,200 connections and up to 3% with 24, with the runtime resequencing per socket under a lock (under 0.5% of cycles in the paper).
- iokerneld pins itself to the first non-zero core of socket 0 and gives that core's hyperthread sibling to Linux and its control thread; running an app on a different NUMA node fails with 'base library per-thread init failed, ret = -12' (fix: numactl, issue #6), and setup_machine.sh reserves hugepages on node 0 only.
- Not every primitive wins: in the paper's Table 2 an uncontended mutex costs 37 ns versus 30 ns for pthreads and 24 ns for Go; each uthread gets a 128 KB stack plus a 128 KB guard region.

## Known shortcomings

- Research runtime needing a dedicated IOKernel core, DPDK NICs and applications ported to its threading API. The README says it is no longer maintained (successor: Caladan). No compiler versions or baseline flags stated.
- A kernel-bypass runtime with its own tcp_/udp_ API, no HTTP layer. TCP stack has no congestion control and no window scaling (#6). Rust bindings need a 2021 nightly (llvm_asm removed in 2022), which also blocks rebuilding the benchmark app (#10). Repo moved to DPDK 19.11 after the paper (18.11). Unmaintained since 2021 (notice added 2024-11). x86-64, one socket only; panics with hyperthreading off unless built with CORES_NOHT. Uncontended mutex slower than pthreads and Go in its own table. Apps must disable preemption around thread-local accesses. Caladan is the maintained successor.

## Caveats and trade-offs

The README says 'This repository is no longer maintained' and points to the successor shenango/caladan. The last commit (2024-11-05) only adds that README notice, so the entry stays marked abandoned. By commit age alone (about 23 months) the rule would give 'stale'. The benchmark_url abstract page has only the qualitative claim; the numbers are in the paper PDF. ZygOS reaches higher peak memcached throughput than Shenango, but at a high latency cost. At memcached's very short service times (&lt;2 us) the IOKernel becomes the bottleneck. Shenango dedicates a full core (2 hyperthreads) to the IOKernel. The main win is CPU efficiency (batch throughput recovered) at equal tail latency, not raw speed over kernel-bypass stacks. The successor Caladan (shenango/caladan, Apache-2.0, 200 stars, pushed 2026-09-25) was published at OSDI'20, not NSDI'20: https://www.usenix.org/conference/osdi20/presentation/fried. Its abstract claims an 11,000x tail-latency reduction vs Parties (580 ms to 52 us).

Requires DPDK and a dedicated IOKernel scheduling process; kernel-bypass core reallocation adds operational complexity

## Maintenance

Declared unmaintained by its authors (last code change 2021-03-25; README notice 2024-11-05) with Caladan as the active successor; Apache-2.0 (the unused ksched kernel module is GPL), so the code can be copied, but building it needs a patched DPDK 19.11 and a 2021 Rust nightly, which makes it research code, not a library to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed NSDI'19 paper (PDF linked from the benchmark_url page) reports numeric wins against Linux and ZygOS on stated hardware (Xeon E5-2650v4, Intel 82599ES). The repo has benchmark code (apps/synthetic with linux-server/linux-client modes, apps/bench with gcc/g++ -O3 Makefiles), but the paper states no compiler versions or flags, and none for the baseline builds (memcached 1.5.6, gdnsd 2.4.0, ZygOS/Linux spin-servers from the ZygOS repo), so it is not A.
- **Verifier notes:** Tier B confirmed, and numbers are now filled in from the paper PDF. The strongest baseline number is 6.33x DNS throughput vs Linux gdnsd. The abandoned tag is kept because the maintainers' README declares it unmaintained; by the commit-age rule alone it would be 'stale', so the orchestrator may want to decide. Caladan (OSDI'20, with numbers) may deserve its own entry; the searcher's 404 came from using the wrong venue (NSDI'20).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/conference/nsdi19/presentation/ousterhout>
  - <https://www.usenix.org/system/files/nsdi19-ousterhout.pdf>
  - <https://github.com/shenango/shenango>
  - <https://github.com/shenango/caladan>
  - <https://www.usenix.org/conference/osdi20/presentation/fried>
- **Sources the enricher read:**
  - <https://github.com/shenango/shenango>
  - <https://github.com/shenango/shenango/blob/master/README.md>
  - <https://github.com/shenango/shenango/blob/master/Makefile>
  - <https://github.com/shenango/shenango/blob/master/dpdk.sh>
  - <https://github.com/shenango/shenango/blob/master/scripts/setup_machine.sh>
  - <https://github.com/shenango/shenango/blob/master/iokernel/cores.c>
  - <https://github.com/shenango/shenango/blob/master/iokernel/main.c>
  - <https://github.com/shenango/shenango/blob/master/runtime/sched.c>
  - <https://github.com/shenango/shenango/blob/master/runtime/defs.h>
  - <https://github.com/shenango/shenango/blob/master/runtime/cfg.c>
  - <https://github.com/shenango/shenango/blob/master/runtime/preempt.c>
  - <https://github.com/shenango/shenango/blob/master/inc/runtime/thread.h>
  - <https://github.com/shenango/shenango/blob/master/inc/runtime/tcp.h>
  - <https://github.com/shenango/shenango/blob/master/inc/runtime/udp.h>
  - <https://github.com/shenango/shenango/blob/master/inc/runtime/sync.h>
  - <https://github.com/shenango/shenango/blob/master/inc/runtime/preempt.h>
  - <https://github.com/shenango/shenango/blob/master/inc/runtime/smalloc.h>
  - <https://github.com/shenango/shenango/blob/master/ksched/ksched.c>
  - <https://github.com/shenango/shenango/blob/master/shim/README>
  - <https://github.com/shenango/shenango/blob/master/bindings/cc/Makefile>
  - <https://github.com/shenango/shenango/blob/master/bindings/cc/thread.h>
  - <https://github.com/shenango/shenango/blob/master/bindings/rust/Cargo.toml>
  - <https://github.com/shenango/shenango/blob/master/bindings/rust/src/lib.rs>
  - <https://github.com/shenango/shenango/blob/master/apps/bench/Makefile>
  - <https://github.com/shenango/shenango/blob/master/apps/synthetic/Cargo.toml>
  - <https://github.com/shenango/shenango/issues>
  - <https://github.com/shenango/shenango/issues/3>
  - <https://github.com/shenango/shenango/issues/5>
  - <https://github.com/shenango/shenango/issues/6>
  - <https://github.com/shenango/shenango/issues/9>
  - <https://github.com/shenango/shenango/issues/10>
  - <https://github.com/shenango/shenango/issues/12>
  - <https://github.com/shenango/shenango/commits/master>
  - <https://www.usenix.org/system/files/nsdi19-ousterhout.pdf>
  - <https://github.com/DPDK/dpdk/commit/7001c8fdb27357c67147c0a13cb3826e48c0f2bf>
  - <https://github.com/rust-lang/rust/pull/92816>
  - <https://github.com/shenango/caladan>
  - <https://github.com/shenango>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/shenango/shenango`) · [data/wave5/enrich/raw/github_com_shenango_shenango.json](../../../data/wave5/enrich/raw/github_com_shenango_shenango.json) (enrichment confidence 0.8)

</details>
