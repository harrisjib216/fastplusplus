# Machnet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> DPDK kernel-bypass messaging sidecar for cloud VMs; 2.6x lower median and 7.4x lower p99.9 RTT than Linux TCP.

| | |
|---|---|
| **Beats** | Linux kernel TCP/IP stack (sockperf with Nagle disabled for microbenchmarks; kernel-TCP builds of a FASTER KV server and of Hashicorp Raft's transport) |
| **Claimed result** | 'Linux TCP's latency is 2.6x, 4.2x, and 7.4x higher than Machnet at median, p99, and p99.9' (64 B echo; Machnet median 27 us). FASTER KV: '3.3x higher throughput, with 700K RPS compared to Linux TCP's 210K RPS', and at 210K RPS a p99 of 50 us vs 250 us (80% lower), using 2 cores vs 100% of all 8 for Linux. Go Raft: 34% lower median latency and 37% lower p99 (p50 185 us vs 282 us, p99 625 us vs 1000 us). |
| **Workload** | Round-trip latency of 64 B echo messages between two Azure F8s_v2 VMs in the same availability zone, one message in flight (Fig. 10). Also a single-threaded FASTER KV server doing 100% GETs over 100M 8-byte keys (Fig. 6), and Hashicorp's Go Raft replicating 80 B commands across 3 VMs (Fig. 8). |
| **Metric** | latency |
| **Hardware** | Azure F8s_v2 VMs (8 vCPUs, 16 GB DRAM) with accelerated networking, Ubuntu 22.04.2, Linux kernel 6.2, same region and availability zone, no proximity placement groups. Hugepages and pinned stack processes for the DPDK stacks; no isolcpus or IRQ steering. The CPU model is not stated. The repo's PERFORMANCE_REPORT lists the Azure F8s_v2 vNIC as CX4-Lx with the netvsc PMD. |
| **Compiler and flags** | Not stated in the paper. The repo's src/CMakeLists.txt Release build uses C++20 with -O3 -DNDEBUG -fno-rtti -fno-exceptions and needs DPDK 23.11. The Docker image builds on Ubuntu 22.04 with build-essential; no compiler version is pinned. |
| **Adoption** | 162 stars, 33 forks. eRPC's README opens with a Dec 2023 news line telling users to check out Machnet. |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/microsoft/machnet) · [benchmark](https://arxiv.org/pdf/2502.09281) |

## Verdict

The source is the first-party arXiv v1 preprint (Feb 2025; the figures still say 'CNet'). Setup: a single-threaded 64 B echo between two Azure F8s_v2 VMs (8 vCPU, accelerated networking, Ubuntu 22.04.2, kernel 6.2, same AZ, no placement groups), with one pinned Machnet engine core, hugepages, and no isolcpus or IRQ steering. Machnet measured 27/32/49 us p50/p99/p99.9 against 70/134/365 us for kernel TCP via sockperf with Nagle off. A single-threaded FASTER GET server did 700K vs 210K RPS, and Go Raft had a 185 vs 282 us median. The compiler and CPU model are not stated, the FASTER and Raft ports are not in the repo, and the peer-reviewed ASPLOS '26 numbers were not checked.

## Use it when

- Latency-critical request/response between services you own on Azure, AWS or GCP VMs in the same subnet and availability zone, where you can spare one engine core and a second NIC per VM. The paper's examples are KV serving (a single-threaded FASTER GET server at 700K vs 210K RPS) and Raft replication.
- Small messages (64 B-32 KB) where kernel TCP tail latency dominates. The paper measured 64 B echo on Azure F8s_v2 at 27/32/49 us p50/p99/p99.9, against 70/134/365 us for Linux TCP.
- Cloud VMs whose vNICs lack flow steering or RSS reconfiguration, where eRPC-, TAS- or Demikernel-style stacks will not run, or where several processes or languages (Go, Rust, C#, JS, C/C++) must share one DPDK NIC.
- Small VMs where kernel-stack CPU is the bottleneck. At FASTER's peak the paper reports 2 cores busy with Machnet against all 8 with Linux TCP.

## Skip it when

- Any peer that is not running Machnet, such as browsers, third-party clients, or gRPC, HTTP and WebSocket ecosystems. TCP interop exists only as unmerged PRs #54-#56 (2026).
- Traffic across subnets or regions. Maintainers confirm in issue #50 that Machnet only ARP-resolves hosts on the same subnet and cannot route via a gateway. It is IPv4-only.
- Multi-engine scaling from main. Issue #49 reports machnet_connect failures with engine_threads &gt; 1 (on AWS), and the maintainers point to the experimental rss_blast branch. The paper's 2 Mrps with 4 engines is not reproducible from main as shipped.
- vNICs without IPv4+UDP TX checksum offload, such as GCP gVNIC gve 1.0.0 (issue #51). Main hits LOG(FATAL) in pmd.cc, even though the paper claims a software-checksum fallback on GCP.
- Networks where you need a hardened transport. The Swift congestion-control block is marked 'first-cut' and never changes its 32-packet initial window. RTOs are checked by a 1 s slow timer, and a flow is torn down after 3 RTO retransmits with no RST sent. There is no encryption.

## How it is fast

It uses DPDK kernel bypass with poll-mode drivers (netvsc on Azure, ENA, gVNIC, mlx5, ice/iavf). Each core runs one busy-polling engine thread with its own NIC RX/TX queue pair, and engines share no flow state, so the data path has no syscalls, interrupts or kernel TCP processing. The app and the stack talk through lock-free rings (jring, modelled on rte_ring) in hugepage shared memory. The paper puts each one-way crossing at \~250 ns, which accounts for most of Machnet's 2 us median gap to eRPC. The transport is a lightweight connection-oriented protocol with a 256-packet SACK bitmap, fast and RTO retransmit, and hardware IPv4/UDP checksum offload. Flows are pinned to an engine by picking UDP source ports whose Toeplitz RSS hash lands on that engine's queue. On main this uses the NIC's RSS key via rte_softrss. The paper's 'RSS--' SYN-spraying variant, for vNICs that hide the key, lives on the experimental rss_blast branch.

## Compared with alternatives

Pick Machnet over eRPC on public-cloud VMs whose vNICs lack RSS reconfiguration or flow steering, or when several processes or languages must share one NIC. eRPC allows one process per NIC and was \~2 us faster at median in the same paper, so prefer eRPC on bare metal or RDMA. Choose HomaModule or grpc_homa for bare-metal clusters where you can load a kernel module, and brpc, Kitex or DRPC when peers must speak gRPC or HTTP or sit outside your fleet.

## Integration

| | |
|---|---|
| **Form** | shared lib (libmachnet_shim.so, C ABI) + separate sidecar process (prebuilt GHCR Docker image or CMake build) |
| **Dependencies** | DPDK 23.11.x (CMake requires libdpdk &gt;=23.11 &lt;24.0), rdma-core (stable-v40 built from source for Mellanox NICs), hugepages, and a dedicated second NIC bound to uio_hv_generic (Azure) or vfio-pci. Git submodules: glog, gflags, googletest, google benchmark, HdrHistogram_c, xxHash. Also needs nlohmann-json, libnl, libhugetlbfs and uuid-dev. The prebuilt image needs Docker and a GitHub PAT with read:packages. |
| **Minimum toolchain** | C++20 for the sidecar and C11 for the shim, built with -fno-rtti -fno-exceptions. GCC 10+ (INTERNAL.md requires gcc-10 on Ubuntu 20.04; the docker image uses Ubuntu 22.04's default). CMake, plus Meson and Ninja for DPDK. |
| **Platforms** | Linux only (the Windows port exists only on unmerged branches). x86-64, with docker-bake targets up to x86-64-v4, and arm64 images. Tested on Azure accelerated networking (CX4-Lx via netvsc), AWS ENA, GCP gVNIC, and bare-metal Intel E810 (ice/iavf), ConnectX and BlueField-2 (mlx5). The NIC must offer IPv4/UDP TX checksum offload. |
| **Thread safety** | Use one channel per application thread (the README says to call machnet_attach in every thread). The send path uses a multi-producer ring. Receive uses a single-consumer ring, and each channel's control request id is a plain increment, so do not share a channel across threads for recv or connect. Control-socket requests are documented as thread-safe. Each engine's Run() loop is documented as not thread-safe; there is one thread per engine. |
| **Drop-in for the baseline** | false. It replaces kernel TCP only between Machnet peers. Apps must be ported from BSD sockets to machnet_\* message calls, and the wire protocol is Machnet-over-UDP, not TCP. |

## Gotchas

- Connection setup on main is slow. machnet_connect and machnet_listen queue a control request, and the shim polls for the reply with sleep(1) between tries (up to 10). The engine only drains control requests on its slow timer, kSlowTimerIntervalUs = 1000000 (the code comment wrongly says '2ms'). Inferred from the code, expect about 1 s or more per connect or listen, not the \~1 ms the paper measured with a 50 us interval.
- machnet_recv never blocks on main; it returns 0 when nothing is queued. The paper's blocking receive (sem_wait) exists only on the go-blocking branch, so apps busy-poll. The paper shows p99 spiking above 10 ms when several polling threads share one core.
- Payloads are copied into and out of shared-memory buffers on every send and recv, so it is not zero-copy. machnet_send returns a bare -1 when the ring is full; there is no retry yet (a TODO), and errors are mostly undifferentiated -1 (issue #5).
- The machnet.h and flow.h comments promise 'end-to-end encrypted' delivery, but main has no crypto code. Traffic is plaintext UDP with a Machnet header.

## Known shortcomings

- Main does not match the paper: RSS-- SYN spraying lives only on the stale rss_blast branch (main still uses the NIC RSS key, which the paper says some cloud vNICs can't support); blocking receive only on go-blocking; the 50 us control interval isn't shipped (slow timer is 1 s, shim polls with sleep(1)), so connect/listen likely take \~1 s, not \~1 ms. More than one engine thread breaks connect on main (#49), so the paper's 2 Mrps with 4 engines can't be reproduced. Same-subnet IPv4 only, no gateway routing (#50). Aborts on GCP gVNIC without TX checksum offload (#51), contrary to the paper's software fallback. Prototype transport: 'first-cut' Swift CC with a fixed 32-packet window, flows torn down after 3 RTOs without RST, plaintext UDP despite an 'end-to-end encrypted' header comment, copying send/recv, bare -1 on full ring. Last code change on main 2024-09 (2026 commits are README edits); TCP interop PRs unmerged. Tier C: preprint only, CPU/compiler not stated, FASTER and Raft ports absent, untuned Linux TCP baseline, \~2 us slower than eRPC at median.

## Caveats and trade-offs

The numbers come from arXiv v1 (Feb 2025, 'Fast Userspace Networking for the Rest of Us', where the figures still label the system 'CNet'). The arXiv API shows no later version as of 2026-09-26. That is a pre-review, first-party version. The peer-reviewed paper is 'Enabling Fast Networking in the Public Cloud', ASPLOS '26, pp. 679-696, DOI 10.1145/3779212.3790158, with a changed author list. Semantic Scholar and OpenAlex mark it Gold OA (CC-BY), and the Machnet docs site links it, but dl.acm.org returned 403 and the PoliMi IRIS record has no file, so the final numbers are unverified. That is why this is tier C; it would be B if the ASPLOS text keeps these comparisons. The Linux baseline is kernel TCP via sockperf, which is not a listed websocket-grpc-rpc baseline (gRPC/uWebSockets/Thrift). That baseline is untuned: Nagle is off, but busy-polling sockets, isolcpus and IRQ steering are not used (the paper omits isolcpus and interrupt steering for all stacks), while Machnet dedicates a polling core. Against eRPC (a known-list project, not a category baseline) Machnet is slower: its median and p99 are within 10% of eRPC and p99.9 within 23%, and its 27 us median is 2 us higher. gRPC was not measured; the paper only asserts that libraries on top of Linux TCP such as gRPC would be slower. Only one Azure region was used, and the paper says cross-cloud numbers are not comparable. The paper's Raft text says '37% lower median p99', and Fig. 8 shows p99 625 vs 1000 us. On the repo side, the benchmark apps in the tree are src/apps/msg_gen, src/apps/rocksdb_server (not in the paper) and bindings/go/msg_gen; the FASTER server and Raft port are not in the tree, and the Linux side used sockperf. The README headline (750K 1KB RPCs/s at 61 us P99.9) has no baseline.

Machnet runs as a separate busy-polling sidecar that takes at least one dedicated engine core. It needs a second, dedicated vNIC per VM that is unbound from the kernel, plus DPDK and hugepages; the prebuilt image comes from GHCR and needs a GitHub token. Apps use its own sockets-like shared-memory message API (machnet_attach/listen/connect/send/recv), not BSD sockets, so they must be ported (C shim with Go, Rust and JS bindings). Its reliable, connection-oriented message protocol only talks to other Machnet peers, so it cannot replace TCP for outside clients. In exchange it runs on basic cloud vNICs (Azure, AWS, GCP) without flow steering, and it supports multiple processes per NIC and blocking receives. Each shared-memory crossing costs \~250 ns, and new connections are handled on a 50 us periodic interval.

## Maintenance

The repo counts as active only through README edits (Jan and Apr 2026) and open TCP PRs (Feb-Aug 2026). Main's code has not changed since the Sept 2024 build_shim.sh fix, and several paper features (RSS--, blocking recv, fast connection setup) live only on stale branches. Treat this MIT-licensed Microsoft Research code, with 162 stars and 13 open issues, as a prototype to vendor and patch, not a supported product.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** arXiv 2502.09281v1 is a first-party, pre-review preprint. Its text and figures give every claimed number: 2.6x/4.2x/7.4x (Fig. 10: 70/134/365 us vs 27/32/49 us), FASTER 700K vs 210K RPS with p99 50 vs 250 us, and Raft p50 185 vs 282 us and p99 625 vs 1000 us. It is not A because the CPU model and compiler are not stated and the FASTER and Raft benchmark code is not public. The peer-reviewed ASPLOS '26 text could not be read, so tier B cannot be confirmed.
- **Verifier notes:** Every claimed number matches arXiv v1. I tried for a readable ASPLOS '26 copy: arXiv API (v1 only), ACM PDF (403), OpenAlex, Semantic Scholar, PoliMi IRIS (no file), Antichi's and Kaffes's pages and the Machnet docs site (links only to ACM). None had the full text, so tier stays C. Metadata checked via GitHub GraphQL: MIT, 162 stars, 33 forks, not a fork or archived, last commit 2026-04-21, so active.
- **Fields the verifier corrected:** `baseline_in_list`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2502.09281>
  - <https://export.arxiv.org/api/query?id_list=2502.09281>
  - <https://github.com/microsoft/machnet>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/README.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/docs/PERFORMANCE_REPORT.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/dockerfiles/ubuntu-22.04.dockerfile>
  - <https://api.crossref.org/works?query.bibliographic=Enabling+Fast+Networking+in+the+Public+Cloud&rows=3>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3779212.3790158?fields=title,openAccessPdf,externalIds,url,isOpenAccess,venue,year>
  - <https://api.openalex.org/works/doi:10.1145/3779212.3790158>
  - <https://re.public.polimi.it/handle/11311/1314031>
  - <https://gianniantichi.github.io/publications/>
  - <https://www.cs.columbia.edu/~kkaffes/>
  - <https://machnett.github.io/machnet-docs/>
  - <https://raw.githubusercontent.com/erpc-io/eRPC/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/microsoft/machnet>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/README.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/ext/machnet.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/ext/machnet.c>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/ext/machnet_common.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/include/cc.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/include/flow.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/include/channel.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/include/machnet_engine.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/core/drivers/dpdk/pmd.cc>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/apps/machnet/README.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/apps/machnet/main.cc>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/Makefile>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/build_shim.sh>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/docs/PERFORMANCE_REPORT.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/main/docs/INTERNAL.md>
  - <https://raw.githubusercontent.com/microsoft/machnet/rss_blast/src/include/machnet_engine.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/rss_blast_measurement/src/include/machnet_engine.h>
  - <https://raw.githubusercontent.com/microsoft/machnet/go-blocking/src/ext/machnet.c>
  - <https://github.com/microsoft/machnet/issues/5>
  - <https://github.com/microsoft/machnet/issues/32>
  - <https://github.com/microsoft/machnet/issues/49>
  - <https://github.com/microsoft/machnet/issues/50>
  - <https://github.com/microsoft/machnet/issues/51>
  - <https://github.com/microsoft/machnet/issues>
  - <https://github.com/microsoft/machnet/pulls>
  - <https://github.com/microsoft/machnet/branches>
  - <https://arxiv.org/pdf/2502.09281>
  - <https://crates.io/api/v1/crates/machnet>
  - <https://hn.algolia.com/api/v1/search?query=machnet&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=machnet%20dpdk&tags=comment>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/microsoft/machnet`) · [data/wave5/enrich/raw/github_com_microsoft_machnet.json](../../../data/wave5/enrich/raw/github_com_microsoft_machnet.json) (enrichment confidence 0.8)

</details>
