# picoquic-DPDK (Tyunyayev kernel-bypass fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Research fork of picoquic that swaps kernel UDP sockets for DPDK; about 3x picoquic single-connection goodput on 100 GbE.

| | |
|---|---|
| **Beats** | picoquic |
| **Claimed result** | Primary paper: "Compared to the original picoquic implementation, we see a 3x improvement" in single-connection goodput (abstract: "improving the throughput by a 3x factor"). For handshakes with 0-byte requests, picoquic-dpdk handles up to 6000 requests/s while picoquic manages about half that. The paper also says picoquic-dpdk on 1 core beats quiche, quicly and msquic; msquic reaches 10.6 Gbps with a 3-core pipeline. |
| **Workload** | One QUIC connection downloading 20 GB (a picoTLS TCP+TLS reference ran a 30 s download) between a client and a server over a 100 Gbps link. AES-128-GCM for all stacks; no disk I/O. picoquic-dpdk ran on 1 core for both I/O and processing, against kernel-socket stacks (original picoquic, quiche, quicly, msquic) in 1-core and 2-core-pipeline setups. A separate test measured handshake rate with 0-byte requests. |
| **Metric** | throughput |
| **Hardware** | Two Intel Xeon Silver 4314 CPUs @ 2.4 GHz (client and server) on a 100 Gbps link; the NIC model is not stated in the paper. |
| **Adoption** | 13 stars |
| **Last commit** | 2022-06-01 |
| **Links** | [repository](https://github.com/UCLouvain-ENSG/picoquic-dpdk) · [benchmark](https://research.dial.uclouvain.be/bitstreams/acc87432-c1b7-4646-be09-8169627726d8/download) |

## Verdict

In the CoNEXT-SW '22 paper, one QUIC connection downloads 20 GB with AES-128-GCM between two Xeon Silver 4314 @ 2.4 GHz hosts over a 100 Gbps link. On one core, picoquic-dpdk reached about 15.7 Gbps (read from Fig. 1) versus about 4.8 Gbps for kernel-socket picoquic, which is roughly the paper's stated 3x. It also beat quicly, msquic (10.6 Gbps with a 3-core pipeline) and quiche, and handled about 2x picoquic's handshake rate. The paper names no compiler; the repo's CMakeLists builds with -O3 -march=native.

## Use it when

- Lab or research testbed with a dedicated DPDK-capable NIC (the paper used 100 GbE between two Xeon Silver 4314 hosts) where you want one core to push one QUIC connection well past 10 Gbps.
- Bulk single-connection downloads measured by goodput: the paper's 20 GB AES-128-GCM transfer reached roughly 15-16 Gbps on 1 core (read from Fig. 1), against about 5 Gbps for kernel-socket picoquic.
- Handshake-rate experiments: up to 6000 zero-byte requests/s, about double stock picoquic in the paper.
- You already have picoquic-based C code and want to measure how much of your cost is kernel I/O rather than crypto or protocol processing.
- Multi-core server scale-out through RSS sharding (one picoquic context per lcore and queue), as long as you do not need connection migration or multipath.

## Skip it when

- Production or internet-facing services: abandoned since 2022, built on what the maintainer calls 'some random base git commit' of picoquic, and missing years of upstream fixes.
- Anything without dedicated NIC access. The maintainer says it cannot run locally or without a real device, and it needs root, hugepages and a busy-polling core; a VM without SR-IOV or passthrough will not work.
- Apps that need connection migration or multipath on the multi-threaded server; the README says the sharded mode does not support either.
- You need numbers that others have reproduced. Jaeger et al. (IFIP Networking 2023) could not reach the reported picoquic goodput and could not easily reproduce the optimizations.
- Throughput with 2 cores on kernel TCP is acceptable: in the same figure, picoTLS over kernel TCP with a 2-core pipeline reached about 20 Gbps, above picoquic-dpdk's 1-core result.

## How it is fast

Kernel bypass with DPDK. It busy-polls the NIC with rte_eth_rx_burst, so there are no interrupts, no syscalls, no sk_buff and no user/kernel copy. Packets move in batches: the paper receives up to 32 per burst, and the -@/-\* flags set RX and TX batch sizes. picoquic writes each outgoing QUIC packet straight into the mbuf at the UDP-payload offset, headers are copied in front, and packets are queued with rte_eth_tx_buffer and flushed together. The paper's profile shows server I/O falling from 18.7% to 5.7% of CPU cycles, which leaves those cycles for crypto and protocol work.

## Compared with alternatives

Pick it over upstream picoquic only when you control a DPDK NIC and need single-core goodput; upstream is maintained and uses kernel sockets. Against the tumi8 kernel-bypass forks (LSQUIC-DPDK, quiche-DPDK), pick this one if your code is already on picoquic's C API or you need its RSS-sharded multi-core server. Their results come from a different 10G testbed, so the numbers cannot be compared directly.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | DPDK (libdpdk via pkg-config), picotls (a matching commit; a later ENSG commit says the picotls API changed), OpenSSL, pthreads |
| **Minimum toolchain** | CMake 2.8.11+; C11/gnu99 GCC or Clang; CMakeLists hard-codes -O3 -march=native -msse4 |
| **Platforms** | Linux with a DPDK-supported NIC; x86-64 as shipped (-msse4 in default flags); has #if branches for DPDK versions before and after 21.11 |
| **Thread safety** | One picoquic context per DPDK lcore and RX/TX queue, sharded by RSS or rte_flow (-r); no shared state between cores is documented. |
| **Drop-in for the baseline** | partial — the picoquic connection/stream callback API is unchanged, but the packet loop is replaced by picoquic_packet_loop_dpdk(), which needs DPDK EAL setup, port/queue/mempool/tx_buffer arguments and peer MAC handling |

## Gotchas

- The built-in L2/L3 layer is minimal. It learns peer MACs from incoming packets into a fixed table (20 entries in this repo, 256 in the ENSG copy), ignores ICMPv4, and makes the client pass the server MAC with -A.
- Unit tests are not maintained. The maintainer said in October 2025 that they never ran the test suite, and an Ubuntu 24.04 / DPDK 21.11.9 report shows many picoquic_ct failures and a segfault in the non-DPDK demo client.
- The no-encryption (memcpy AEAD) variant used in the thesis measurements is not in either repo. It was a local patch to picotls aead_encrypt/aead_decrypt.
- TX-ring overflow only prints 'PACKET DROPPED!' from the drop callback, and the RX loop polls forever, so each worker core sits at 100% even when idle.

## Known shortcomings

- Needs DPDK kernel bypass (dedicated NIC, one core per connection in the paper). A later paper (arXiv:2309.16395) could not reproduce the reported goodput. No compiler or flags stated. Research code, last commit 2022; the paper's code lives at UCLouvain-ENSG/picoquic-dpdk, the IPNetworkingLab repo is an earlier thesis version.
- The 3x is read off a figure (\~15.7 vs \~4.8 Gbps); kernel picoTLS over TCP with 2 cores reaches \~20 Gbps, beating it. The maintainer said in 2025 the test suite was never run and the base picoquic commit is arbitrary; many picoquic_ct failures and a demo segfault reported on Ubuntu 24.04. Enrichment confidence 0.35 (below the 0.4 flag threshold).

## Caveats and trade-offs

The primary paper confirms the 3x figure against plain kernel-socket picoquic, measured with one connection, one core and a 20 GB download on a 100 Gbps link. Compiler and flags are not stated. The paper names https://github.com/UCLouvain-ENSG/picoquic-dpdk as the official code (MIT, 3 stars, last commit 2022-10-31), with scripts in UCLouvain-ENSG/picoquic-dpdk-experiments (NPF, no license). This IPNetworkingLab repo is the earlier master's-thesis version (last commit 2022-06-01), so the paper's numbers may belong to the ENSG repo rather than this one. The repo is not a GitHub-network fork: it is a copied derivative of private-octopus/picoquic. Jaeger et al. (arXiv:2309.16395, IFIP Networking 2023) say they 'are not able to reach similar goodput as reported by Tyunyayev et al.' for picoquic and could not easily reproduce the optimizations. DPDK needs dedicated NIC queues and busy-polling cores, and the paper is a 3-page student-workshop paper.

DPDK kernel bypass requires a dedicated NIC/queue, hugepages, and root; README describes the project as 'work in progress'. A companion experiments repo (UCLouvain-ENSG/picoquic-dpdk-experiments) is explicitly set up to compare it against quicly, quiche, and msquic directly, but the specific numeric results for those comparisons could not be retrieved this session.

## Maintenance

Abandoned research code: this repo was last pushed 2022-06-01 and the paper-cited ENSG copy 2022-10-31. It is MIT-licensed, but you get it as a patched picoquic tree tied to 2022-era DPDK and picotls, not as a reusable library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B. The primary peer-reviewed paper is now in hand (Tyunyayev, Piraux, Bonaventure, Barbette, 'A High-Speed QUIC Implementation', ACM CoNEXT-SW '22; open-access copy on UCLouvain DIAL). Its evaluation says 'Compared to the original picoquic implementation, we see a 3x improvement' in single-connection goodput on two Xeon Silver 4314 machines over a 100 Gbps link. It is not A: the public NPF harness (UCLouvain-ENSG/picoquic-dpdk-experiments, repo/\*.repo and quic_tester_compare.npf) exists, but no compiler or flags are stated; the builds are a plain 'cmake . && make'.
- **Verifier notes:** Opened the primary paper through the OpenAlex/Semantic Scholar green open-access link (hdl 2078.1/276119, which resolves to UCLouvain DIAL); dl.acm.org still returns 403. The orchestrator may want to switch repo_url to UCLouvain-ENSG/picoquic-dpdk, the repo the paper cites (same authors, MIT, abandoned since 2022-10). License MIT, 13 stars, last commit 2022-06-01 and 'abandoned' were all checked with gh and are correct.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2309.16395>
  - <https://arxiv.org/pdf/2309.16395>
  - <https://github.com/IPNetworkingLab/picoquic-dpdk>
  - <https://api.crossref.org/works?query.bibliographic=A+High-Speed+QUIC+Implementation+Tyunyayev&rows=5>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3565477.3569154?fields=title,openAccessPdf,externalIds,url,abstract,isOpenAccess>
  - <https://api.openalex.org/works/https://doi.org/10.1145/3565477.3569154>
  - <http://hdl.handle.net/2078.1/276119>
  - <https://research.dial.uclouvain.be/entities/publication/1f851d57-1304-41a0-b869-c4a842e3872c>
  - <https://research.dial.uclouvain.be/bitstreams/acc87432-c1b7-4646-be09-8169627726d8/download>
  - <https://perso.uclouvain.be/tom.barbette/>
  - <https://perso.uclouvain.be/tom.barbette/publications/>
  - <https://perso.uclouvain.be/tom.barbette/research-project/>
  - <https://perso.uclouvain.be/tom.barbette/ensg/>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk-experiments>
  - <https://github.com/ntyunyayev/quic_implems_cmp>
- **Sources the enricher read:**
  - <https://github.com/IPNetworkingLab/picoquic-dpdk>
  - <https://github.com/IPNetworkingLab/picoquic-dpdk/blob/main/README.md>
  - <https://github.com/IPNetworkingLab/picoquic-dpdk/blob/main/picoquic/sockloop_dpdk.c>
  - <https://github.com/IPNetworkingLab/picoquic-dpdk/blob/main/dpdk_picoquicfirst/dpdk_picoquicdemo.c>
  - <https://github.com/IPNetworkingLab/picoquic-dpdk/commits/main>
  - <https://github.com/IPNetworkingLab/picoquic-dpdk/issues/1>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/blob/main/README.md>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/blob/main/CMakeLists.txt>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/blob/main/picoquic/sockloop_dpdk.c>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/blob/main/dpdk_picoquicfirst/dpdk_picoquicdemo.c>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/blob/main/dpdk_picoquicfirst/dpdk_server.c>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/commits/main>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk/issues/1>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk-experiments>
  - <https://github.com/UCLouvain-ENSG/picoquic-dpdk-experiments/blob/main/.gitmodules>
  - <https://research.dial.uclouvain.be/bitstreams/acc87432-c1b7-4646-be09-8169627726d8/download>
  - <https://arxiv.org/pdf/2309.16395>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ipnetworkinglab/picoquic-dpdk`) · [data/wave5/enrich/raw/github_com_ipnetworkinglab_picoquic_dpdk.json](../../../data/wave5/enrich/raw/github_com_ipnetworkinglab_picoquic_dpdk.json) (enrichment confidence 0.35)

</details>
