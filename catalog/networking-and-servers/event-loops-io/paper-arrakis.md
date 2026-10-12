# Arrakis

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Research OS (Barrelfish fork) giving apps direct SR-IOV NIC and storage queues; beat tuned Linux 3.8 I/O by 1.7-9x.

| | |
|---|---|
| **Beats** | epoll / Linux kernel I/O stack (Linux 3.8, Ubuntu 13.04, tuned ixgbe 3.17.3: sockets + epoll network path and VFS write/fsync storage path) |
| **Claimed result** | Abstract: 2-5x lower latency and 9x higher throughput for Redis relative to a well-tuned Linux implementation (2x read latency, 5x write latency, 9x write throughput). Table 2: Redis read-hit latency 8.67 us Linux vs 4.07 us Arrakis/P, durable write 163.14 us vs 31.51 us (about 2.1x and 5.2x, derived from page data). Other results: UDP echo 2.3x (Arrakis/P) and 3.9x (Arrakis/N); memcached 1.7x on one core; haproxy 2.2x vs Linux and 2x vs Linux with SEPOLL (speculative epoll) on one core; IP middlebox 2.6x. |
| **Workload** | Redis 2.8.5 persistent NoSQL store (GET/SET, 1 KB values, 65,536 keys, every SET persisted individually, 1,600 connections, single core), Arrakis/P (POSIX) vs Linux; also a UDP echo server, memcached 1.4.15 (90/10 get/set), haproxy 1.4.24 HTTP load balancing, and a raw-IP load-balancing middlebox. |
| **Metric** | throughput |
| **Hardware** | Six-machine cluster: 6-core Intel Xeon E5-2430 (Sandy Bridge) @ 2.2 GHz, Intel X520 (82599) 10 GbE, Intel MegaRAID RS3DC040 with 1 GB flash-backed DRAM in front of a 100 GB Intel DC S3700 SSD, Dell PowerConnect 8024F 10 GbE switch |
| **Adoption** | 267 stars (UWNetworksLab/arrakis); OSDI 2014 Best Paper |
| **Last commit** | 2014-05-22 |
| **Links** | [repository](https://github.com/UWNetworksLab/arrakis) · [benchmark](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-peter_simon.pdf) |

## Verdict

The OSDI'14 paper ran a single server (6-core Xeon E5-2430 at 2.2 GHz, Intel X520 10GbE, MegaRAID RS3DC040 with 1 GB flash-backed DRAM over a DC S3700 SSD) against Ubuntu 13.04 / Linux 3.8 with ixgbe 3.17.3 and RSS off. On one core, Redis 2.8.5 read-hit latency fell from 8.67 to 4.07 us and durable SET from 163.14 to 31.51 us, with about 9x SET throughput (read from the Fig. 6 bar chart, not tabulated). Other results: UDP echo 2.3x (POSIX) and 3.9x (native), memcached 1.7x on one core, haproxy 2.2x (2x against SEPOLL), and a raw-IP middlebox 2.6x. No compiler or flags are given, and the Arrakis Redis used Caladan (a 109-line change), so the benchmark is not an unmodified POSIX port.

## Use it when

- Studying, reproducing or extending the OSDI'14 control-plane/data-plane split. The tree has the 82599 SR-IOV PF/VF drivers, the VT-d driver, the Arranet stack, the TenaciousD log and the UDP echo benchmark from Sec 2 and 4.1.
- Research prototypes on matching hardware (Intel 82599/X520 NIC, Intel MegaRAID RS3 controller, Xeon with VT-d) where you control the whole machine and can boot a Barrelfish-derived OS.
- Small-message request/response servers with one process per core (UDP echo, binary-UDP memcached, Redis-style GET/SET) where per-packet kernel overhead dominates. The gain shrinks as per-request work grows and is gone at about 64 us of processing per packet (Fig. 4).
- Append-only durable writes on a controller with a flash-backed write cache, where fsync overhead dominates latency. In the paper, Redis SET latency fell from 163 us to 31.5 us.

## Skip it when

- Any production service. Arrakis is an OS rather than a library: the last release is 2014-05-14, the project site is an archive, and it says Arrakis was merged back into Barrelfish in 2015.
- Stock Linux hosts. Only the TenaciousD log builds on Linux (a POSIX AIO backend); the network path needs the Barrelfish-based OS, so for kernel bypass on Linux look at the maintained stacks listed as siblings.
- Real TCP traffic over lossy or wide-area paths. Arranet advertises a fixed 11,680-byte window and does no Nagle; I found no retransmission timer or congestion control in arranet.c, and many socket calls and options hit assert(!"NYI").
- Compute-heavy requests or many-core scaling. The advantage disappears at about 64 us of work per packet. Memcached gained 1.7x on one core, and Arrakis throughput dropped on 6 cores because of Barrelfish management processes.
- Hardware outside the tested set. README_ARRAKIS lists only a Dell R520 with a Xeon E5-2430, an X520 and a MegaRAID RS3DC040. The 82599 can filter only on MAC and VLAN, so flows are split by a per-VNIC MAC and then filtered in software, and the RAID controller had no SR-IOV (its physical function was used).

## How it is fast

It uses kernel bypass with hardware protection: SR-IOV virtual functions and the VT-d IOMMU enforce isolation, so recv, send and epoll become library calls with no syscalls, no scheduler wakeups, no software demultiplexing and no socket locks. Per UDP echo, the paper's Table 1 measures 3.36 us on Linux, 1.44 us on Arrakis/P and 0.38 us on Arrakis/N. Each process owns its VNIC queues and runs its own lwIP-derived stack instance (Extaris in the paper, lib/arranet in the repo), so packets stay on the core that runs the app, and Arrakis/N also removes the two POSIX copies by handing out pointers into NIC buffers. On the storage side, the Caladan log persists each entry with one hardware write plus an end-of-entry marker and skips VFS, journal and inode work; this is where most of the Redis durable-write gain comes from (fsync 137.84 us vs 24.26 us).

## Compared with alternatives

Choose Arrakis over mTCP, F-Stack, Seastar or IX only to study or build on its design. Its storage half (per-app virtual storage areas plus a persistent log, measured against write+fsync) is something none of those siblings cover. For a network workload you actually need to run, the maintained sibling stacks are the practical choice, since Arrakis needs its own OS and 2014-era Intel NIC/RAID hardware.

## Integration

| | |
|---|---|
| **Form** | source-drop: the whole OS tree; apps are cross-compiled through a gcc wrapper and linked against static libs (libarranet.a, libposixcompat.a, libe10k_vf.a, libvfs.a) |
| **Dependencies** | Build: GCC 4.x, GNU binutils, GNU make, GHC plus Parsec (for the hake/Mackerel/Flounder tools). Hardware: SR-IOV NIC (Intel 82599/X520), Intel VT-d IOMMU, and an Intel MegaRAID RS3 for the storage path. Boot: a Multiboot bootloader that can load ELF64, or QEMU. |
| **Minimum toolchain** | GCC 4.x (4.4.5 and 4.5.2 known to work), binutils 2.19, GHC 7.4 with Parsec 3.1 (May 2014 PRs patched the tools for GHC 7.6); modern toolchains not documented |
| **Platforms** | x86-64 for the Arrakis additions; tested only on a Dell PowerEdge R520 (Xeon E5-2430) with an Intel X520 and a MegaRAID RS3DC040; boots under QEMU for development. Barrelfish's ARM/SCC ports are not documented for Arrakis. |
| **Thread safety** | Not thread-safe per stack instance. arranet.c keeps global RX state and a single recv/send waitset channel, with comments 'Needs to be per socket later on' and 'Need to lock if multithreaded!'. The paper scales by running one process per core, each with its own VNIC and stack. |
| **Drop-in for the baseline** | partial — Arrakis/P provides POSIX sockets and epoll, so apps can be recompiled for Barrelfish without API changes. But epoll_ctl asserts on EPOLLET, EPOLLONESHOT, EPOLLRDHUP, EPOLLPRI, EPOLLERR and EPOLLHUP (level-triggered only); many socket calls assert NYI; and the storage gain needs code changes (109 lines in Redis to use Caladan). Arrakis/N is a different API. |

## Gotchas

- arranet.c hardcodes lab settings: a static ARP table of the authors' machines (you must edit peers[] and peers_alloc) and an unconditional software UDP filter that accepts only destination ports 1234, 11211 and 11212.
- The paper and the code use different names. The paper's Extaris stack is lib/arranet and its Caladan structures are lib/tenaciousd. Only the log is present (tenaciousd_log_trim asserts NYI; there is no persistent queue), and the ported Redis, memcached and haproxy are not in the tree.
- Protocol mode is global to the process: socket() sets global TCP/UDP/raw accept flags, and the readiness checks branch on the TCP flag, so one process that mixes TCP and UDP sockets looks unsupported.
- Read the numbers carefully. Linux had offloads Arrakis lacked (TSO/LRO, direct cache access, header split). But the baseline is Linux 3.8 sockets+epoll plus kernel fsync, Sec 4.4 says write latency improved by 63% while the abstract says 5x (Table 2 gives about 5.2x), and Caladan on Linux alone gave 5x of the 9x Redis write throughput.

## Known shortcomings

- Research OS (a Barrelfish fork) requiring SR-IOV hardware; abandoned since 2014-05. Much of the Redis write gain comes from the storage path, not epoll. The ported Redis, memcached and haproxy used in the paper are not in the public repo.
- The public network stack (lib/arranet) is demo-grade: hardcoded ARP table of the authors' lab, UDP accepted only on ports 1234/11211/11212, fixed TCP window, no retransmission timer or congestion control found, only level-triggered epoll. The persistent-data library has only the log. Redis needed a 109-line change, and Caladan-on-Linux alone gave 5x of the 9x write gain. Baseline Linux 3.8 (2013).

## Caveats and trade-offs

Research OS (a Barrelfish fork) that needs SR-IOV NICs and IOMMU hardware; it is not a drop-in library. Much of the Redis write win comes from the storage path (fsync 137.84 us vs 24.26 us) and the custom Caladan/TenaciousD log, not just from bypassing epoll. Porting Caladan to Linux alone gave 5x write throughput. Sec 4.4 says 'write latency improves by 63%', which is inconsistent with the abstract's 5x taken from Table 2. The paper says Linux used offloads Arrakis lacked (TSO/LRO/DCA), so the comparison is weighted toward Linux. The public repo (MIT) contains the OS, the Arranet stack, TenaciousD and the UDP echo benchmark, but not the ported Redis, memcached or haproxy. The project site says Arrakis has been merged back into Barrelfish and is no longer maintained separately. No compiler or flags are given.

Requires a custom split-kernel OS (Barrelfish-derived) and virtualized/SR-IOV-capable NIC hardware; not portable to stock Linux; no public source release found.

## Maintenance

Abandoned: the code is frozen at the 2014-05-14 release (last master commit 2014-05-22, a 2017 PR never merged), the project site is an archive saying Arrakis was merged into Barrelfish in 2015, and a 2016 'How to run Arrakis' issue got no guidance. It is MIT-licensed, but using it means building and booting a research OS with GCC 4.x/GHC 7.4 on 2014-era Intel hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B. The OSDI'14 paper (peer-reviewed, Best Paper) measures Arrakis against a tuned Linux 3.8 kernel I/O path, including epoll (Table 2 breaks out epoll/recv/send/fsync costs, and haproxy is compared against Linux with and without SEPOLL). Public code does exist (github.com/UWNetworksLab/arrakis, MIT, with usr/bench/udp_echo), so the no-code cap no longer applies. It is not A: the paper gives no compiler or flags, and the ported Redis, memcached and haproxy builds are not in the public tree.
- **Verifier notes:** Code does exist: arrakis.cs.washington.edu/download points to github.com/UWNetworksLab/arrakis (MIT, 267 stars, not archived, not a GitHub fork, last master commit 2014-05-22). The orchestrator should set repo_url to that URL (repo_url is not a correctable field here) and may re-key the id. All abstract numbers were verified in the paper PDF; the workload is real Redis 2.8.5, not 'Redis-like'.
- **Fields the verifier corrected:** `license`, `usability`, `last_commit`, `maintenance_status`, `stars_or_usage`, `is_fork_of`, `baseline`, `workload`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-peter_simon.pdf>
  - <https://github.com/UWNetworksLab/arrakis>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/README_ARRAKIS>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/LICENSE>
  - <http://arrakis.cs.washington.edu/>
  - <https://arrakis.cs.washington.edu/download/>
- **Sources the enricher read:**
  - <https://github.com/UWNetworksLab/arrakis>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/README>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/README_ARRAKIS>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/include/arranet.h>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/include/arranet_impl.h>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/arranet/arranet.c>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/arranet/Hakefile>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/posixcompat/epoll.c>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/include/tenaciousd/log.h>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/tenaciousd/log.c>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/tenaciousd/README>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/tenaciousd/build.sh>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/lib/tenaciousd/aio_vsic.c>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/include/storage/vsic.h>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/tools/arranet_e10k-cc-wrapper>
  - <https://github.com/UWNetworksLab/arrakis/blob/master/usr/bench/udp_echo/udp_echo.c>
  - <https://github.com/UWNetworksLab/arrakis/commits/master>
  - <https://github.com/UWNetworksLab/arrakis/issues/3>
  - <https://github.com/UWNetworksLab/arrakis/issues/4>
  - <https://github.com/UWNetworksLab/arrakis/issues/6>
  - <https://github.com/UWNetworksLab/arrakis/pull/5>
  - <https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-peter_simon.pdf>
  - <https://arrakis.cs.washington.edu/>
  - <https://arrakis.cs.washington.edu/download/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `paper:arrakis`) · [data/wave5/enrich/raw/paper_arrakis.json](../../../data/wave5/enrich/raw/paper_arrakis.json) (enrichment confidence 0.75)

</details>
