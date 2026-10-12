# LSQUIC-DPDK (tumi8 kernel-bypass fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> LSQUIC 4.2 fork with a zero-copy DPDK datapath; 1.3x kernel MsQuic (GSO+GRO) goodput on single-connection bulk downloads.

| | |
|---|---|
| **Beats** | msquic |
| **Claimed result** | Paper Fig. 2 (plain DPDK, same-implementation pairs, mean of 50 x 8 GiB downloads): LSQUIC-DPDK 10756 Mbit/s vs upstream MsQuic v2.4.8 (kernel UDP with GSO+GRO) 8250 Mbit/s (\~1.30x, derived from page data). MsQuic-DPDK reaches 7983 Mbit/s (\~1.35x, derived), and upstream LSQUIC reaches 3605 Mbit/s (2.98x, printed). With SR-IOV (quic-bypass-paper measurement-data/06-dpdk-integration/processed.csv, Fig. 5): LSQUIC-DPDK 11019 vs MsQuic-DPDK 8118 (\~1.36x) and quiche-DPDK 6168 Mbit/s (\~1.79x) (derived from page data). |
| **Workload** | HTTP/3 download of an 8 GiB file between two bare-metal hosts with 100 Gbit/s Intel E810 NICs, using the extended QUIC Interop Runner (framework/config/bypass-paper/01-implementation-matrix.conf and 06-dpdk-integration.conf). Same-implementation client/server pairs ran 50 repetitions each. Kernel variants used 32x (6815744 B) socket buffers with NIC offloads on. DPDK variants ran on the physical function (ice) or an SR-IOV virtual function (iavf). |
| **Metric** | throughput |
| **Hardware** | Both hosts: Intel Xeon Gold 6421N (32 cores), 512 GiB DDR5, Intel E810-CQDA2 100 Gbit/s NIC, Debian 12 with Linux 6.1.0-17, DPDK v24.11 (paper Appendix Table I). |
| **Compiler and flags** | LSQUIC-DPDK: quic-dpdk-implementations/lsquic-dpdk/build.sh builds BoringSSL 0.20250212.0 and lsquic-dpdk with CMAKE_BUILD_TYPE=Release (-O3 -g0 via lsquic CMakeLists). It builds DPDK commit 1b3bf112 with meson -Dplatform=generic, using GCC from Debian 12 build-essential (version not stated). MsQuic-DPDK: build.ps1 -Static -Tls openssl -Config Release -UseDpdk with CFLAGS/CXXFLAGS=-Wno-error=stringop-overflow. The kernel baselines (MsQuic v2.4.8, LSQUIC, quiche) are built by a private LRZ GitLab CI, so their flags are unpublished. |
| **Adoption** | 0 stars (research artifact accompanying a NOMS 2026 paper) |
| **Last commit** | 2026-02-11 |
| **Links** | [repository](https://github.com/tumi8/lsquic-dpdk) · [benchmark](https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf) |

## Verdict

Two bare-metal hosts (Intel Xeon Gold 6421N, 100 Gbit/s Intel E810, Debian 12, Linux 6.1, DPDK v24.11) each downloaded an 8 GiB file over one connection 50 times, with the same implementation on client and server. LSQUIC-DPDK averaged 10,756 Mbit/s (SD 39), against 8,250 for upstream MsQuic v2.4.8 on kernel UDP with GSO+GRO (1.30x) and 3,605 for upstream LSQUIC (2.98x). On SR-IOV VFs it averaged 11,019 against 8,118 for MsQuic-DPDK (1.36x). LSQUIC-DPDK was a GCC Release build (-O3, compiler version not stated). The kernel baselines came from a private CI with unpublished flags, and the runs used the hq-interop ALPN.

## Use it when

- Point-to-point bulk transfers (multi-GiB, single connection) between hosts you control, with LSQUIC-DPDK at both ends: the 10.8 Gbit/s result is for a DPDK client talking to a DPDK server.
- You already use LSQUIC and packet I/O limits you: upstream LSQUIC has no GSO/GRO, and this fork measured 2.98x its kernel goodput on the same hardware (10,756 vs 3,605 Mbit/s).
- Linux x86-64 hosts with a DPDK-supported NIC (tested: Intel E810 on the ice PF or an iavf SR-IOV VF), hugepages, and a core you can give over to busy polling. SR-IOV lets the kernel keep the rest of the port and was slightly faster (11,019 Mbit/s).
- Research or benchmarking of kernel-bypass QUIC: the Interop Runner configs, build scripts and raw per-run CSVs are public, so you can reproduce the numbers.

## Skip it when

- Only one side can run DPDK. An LSQUIC-DPDK client against a kernel LSQUIC server measured 3,991 vs 3,605 Mbit/s (1.11x). Against a kernel MsQuic server it reached 7,370 Mbit/s, below the 8,250 of plain MsQuic on both ends.
- Internet-facing or production servers. The code is pinned to LSQUIC v4.2.0 (Feb 2025), 21 upstream releases behind v4.10.0. It lacks later fixes such as an ls-qpack use-after-free, rejection of conflicting Content-Length headers, and RST_STREAM stream-limit enforcement. It is research code with 0 stars.
- Many concurrent connections or multi-core scaling. The code allows one engine on one worker lcore and one port (dpdk_init exits otherwise), and uses a fixed 256-entry peer table with linear lookup and no eviction. The client opens a single connection.
- Your baseline is MsQuic with GSO+GRO and you cannot spare a NIC port or VF, hugepages, and a core that polls at 100%. The gain is only 1.30x there, and the paper concludes that GSO/GRO can match DPDK with far less intrusion.
- Multi-hop or shared-bottleneck paths. With DPDK, 99% of LSQUIC's packets leave back-to-back, against 50% spaced at least 2.9 µs apart on the kernel path, so expect bursty traffic.

## How it is fast

Kernel bypass with a run-to-completion busy-poll loop on one DPDK lcore: pull up to 32 packets per rte_eth_rx_burst, feed them to lsquic_engine_packet_in, tick the engine, then flush a 32-packet TX buffer, so there are no syscalls or socket copies. LSQUIC's packet-out memory interface (pmi_allocate) is redirected to hand out space inside hugepage mbufs just past the header offset, so packets are encrypted straight into NIC-visible buffers (zero-copy), and coalesced long-header packets share one mbuf. The paper's perf profile shows the packet-I/O share of CPU falling 90% on the server and 84% on the client, which leaves crypto and file I/O as the new bottlenecks. Upstream LSQUIC has no GSO/GRO, so the gain over it (2.98x) is much larger than over MsQuic, which already uses both offloads (1.30x).

## Compared with alternatives

Pick it over quiche-DPDK and picoquic-DPDK when you want the highest measured kernel-bypass goodput. In the same testbed, LSQUIC-DPDK pairs reached 10,756 Mbit/s against 8,347 for the paper's updated picoquic-DPDK and 5,937 for quiche-DPDK, and 11,019 against 9,070 and 6,168 on SR-IOV. Pick upstream LSQUIC or ngtcp2 instead if you cannot dedicate a NIC port or VF, or you need a current, maintained QUIC stack.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | DPDK (artifact builds commit 1b3bf112; paper uses v24.11) found via pkg-config libdpdk; BoringSSL (artifact pins 0.20250212.0); zlib; CMake. Needs hugepages, root, and a NIC port or SR-IOV VF bound to a DPDK driver. The libevent requirement of upstream's examples is gone. |
| **Minimum toolchain** | CMake 3.0+ (cmake_minimum_required 3.0...3.23); a C compiler that accepts -mssse3 (the artifact uses GCC from Debian 12 build-essential, version not stated); meson/ninja to build DPDK. |
| **Platforms** | Linux x86-64 only as shipped (-mssse3 is hard-coded in bin/CMakeLists.txt); tested only on Intel E810 (ice PF, iavf VF) with Debian 12 / Linux 6.1. Upstream LSQUIC's other platforms do not apply to the DPDK binaries. |
| **Thread safety** | Not thread-safe: one lsquic engine runs on a single DPDK worker lcore. dpdk_init exits if more than one port or worker lcore is configured, and allocate_mbuf uses static global batch state. |
| **Drop-in for the baseline** | no |

## Gotchas

- API break against upstream LSQUIC: lsquic_engine_process_conns() and lsquic_engine_earliest_adv_tick() now take an explicit `now` argument, and pmi_allocate gains an is_long_hdr argument. The kernel-socket event loop and the md5/echo/duck/perf examples were removed, so only the DPDK http_client and http_server build.
- IPv4 packets go out with a UDP checksum of 0, and the IP checksum is computed in software. No checksum or segmentation offloads are enabled; only MBUF_FAST_FREE is requested. The IPv6 receive path passes a NULL peer context to lsquic_engine_packet_in, so treat IPv6 as untested.
- The custom TX error callback only prints 'PACKET DROPPED!' and does not free the unsent mbufs. Registering it replaces DPDK's default callback, which frees them, so a TX-queue overflow leaks mbufs from the 16,383-mbuf pool.
- The client does no ARP resolution: pass the server (or gateway) MAC with -J and the client IP with -x (the error message wrongly says -b). The published runs used the hq-interop ALPN, not h3; the README says h3 and hq should perform alike and that the qif ALPN is untested.

## Known shortcomings

- Research kernel-bypass fork: needs DPDK or SR-IOV with dedicated NICs (tested on Xeon Gold 6421N with a 100G E810). The non-DPDK baseline builds are on a private GitLab and compiler versions are not pinned.
- Uses hq-interop, not h3. The run scripts build LSQUIC_O_FLAG (Cubic, flow-control windows) but never pass it, so the README settings are not what ran. The gain needs DPDK at both ends: DPDK client vs kernel LSQUIC server is 1.11x; vs a kernel MsQuic server it is 7370 Mbit/s, below MsQuic-to-MsQuic 8250. An unpublished XDP variant (7925) is also below kernel MsQuic. Pinned to LSQUIC v4.2.0 (misses later fixes incl. an ls-qpack use-after-free); modified engine API; DPDK datapath only in bin/ examples. Source issues: IPv4 UDP checksum 0, NULL peer context on IPv6 receive, TX drop callback leaks unsent mbufs, one port/lcore, fixed 256-entry peer table, x86-only (-mssse3). Frozen artifact since 2026-02.

## Caveats and trade-offs

Peer-reviewed and published: Spaeth et al., 'Kernel Bypass Surgery: A Viable Procedure for Maximizing QUIC Bandwidth?', NOMS 2026, Rome, pp. 1-8, DOI 10.1109/NOMS69089.2026.11668379. The open preprint is on net.in.tum.de, and the dataset is Zenodo 10.5281/zenodo.18630971. The two msquic-dpdk tables are not inconsistent: 7983 is plain DPDK on the ice PF and 8118 is SR-IOV on the iavf VF, which the paper finds slightly faster. The comparison pits kernel bypass against kernel sockets. LSQUIC-DPDK needs a DPDK-bound NIC port or SR-IOV VF, runs single-threaded with busy polling, and has no GSO/GRO. The authors note that their MsQuic-DPDK datapath enqueues packets one at a time, which handicaps it. Against upstream MsQuic with GSO+GRO, the lead is \~1.30x. GitHub does not mark the repo as a fork, but it is the full LSQUIC tree (based on v4.2.0) with a DPDK datapath.

Same DPDK/SR-IOV deployment complexity as other entries in this family (dedicated NIC/queue, hugepages, root). A separate table in the same dataset (measurement-data/01-implementation-matrix/processed.csv) shows msquic-dpdk NOT beating vanilla kernel msquic (7982 vs 8250 Mbit/s), so DPDK's benefit is very implementation-dependent; only the head-to-head DPDK-vs-DPDK cross-library comparison used here is a clean win for LSQUIC-DPDK.

## Maintenance

A research artifact for a NOMS 2026 paper: the DPDK work (authored 2023-2025) landed in Feb 2026, the last commit is a README note on 2026-02-11, and no issues have been filed. MIT-licensed, and the DPDK glue (\~1,500 lines) is small enough to copy, but it tracks LSQUIC v4.2.0 and has no upstream path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NOMS 2026 paper (now published, DOI 10.1109/NOMS69089.2026.11668379). Its Fig. 2 prints LSQUIC-DPDK 10756 vs upstream MsQuic 8250 and MsQuic-DPDK 7983 Mbit/s. The published processed.csv gives the claimed SR-IOV means (11019 / 8118 / 6168). The framework, configs, LSQUIC-DPDK build script (Release) and CPU (Xeon Gold 6421N) are public. It is not A: the compiler version is not stated, and the kernel MsQuic/LSQUIC/quiche baseline binaries are built from a private LRZ GitLab CI (framework/fetch_artifacts.py), so their flags are not published.
- **Verifier notes:** The DOI-TODO caveat is outdated: the paper is published (Crossref DOI 10.1109/NOMS69089.2026.11668379), and the TUM preprint gives the CPU model, so the hardware is filled in. I added the upstream-MsQuic comparison from paper Fig. 2 because the original claim only compared against the group's own MsQuic-DPDK port. last_commit is 2026-02-11 (the default-branch commit), not the 2026-02-12 push date.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/06-dpdk-integration/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/01-implementation-matrix/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/README.md>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/config/bypass-paper/01-implementation-matrix.conf>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/config/bypass-paper/06-dpdk-integration.conf>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/testbed/testbed_stoi-pact.json>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/implementations.json>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/fetch_artifacts.py>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/lsquic-dpdk/build.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/msquic-dpdk/build.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/evaluation/paper-plots.ipynb>
  - <https://github.com/tumi8/lsquic-dpdk>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/README.md>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/CMakeLists.txt>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/LICENSE>
  - <https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf>
  - <https://www.net.in.tum.de/publications/>
  - <https://api.crossref.org/works/10.1109/noms69089.2026.11668379>
  - <https://zenodo.org/api/records/18630971>
  - <https://ieeexplore.ieee.org/document/11668379>
- **Sources the enricher read:**
  - <https://github.com/tumi8/lsquic-dpdk>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/README.md>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/CMakeLists.txt>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/CMakeLists.txt>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/dpdk.c>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/dpdk.h>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/sockloop_dpdk.c>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/socket_loop.h>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/prog.c>
  - <https://github.com/tumi8/lsquic-dpdk/blob/main/bin/http_server.c>
  - <https://github.com/tumi8/lsquic-dpdk/commits/main>
  - <https://github.com/tumi8/lsquic-dpdk/commit/f2848806>
  - <https://github.com/tumi8/lsquic-dpdk/commit/667560a6>
  - <https://github.com/tumi8/lsquic-dpdk/commit/fd3d8d0c>
  - <https://github.com/tumi8/lsquic-dpdk/commit/83526046>
  - <https://github.com/tumi8/lsquic-dpdk/branches>
  - <https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/lsquic-dpdk/build.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/lsquic-dpdk/run-server.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/lsquic-dpdk/run-client.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/lsquic-dpdk/setup-env.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/lsquic-dpdk/README.md>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/06-dpdk-integration/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/01-implementation-matrix/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/config/bypass-paper/06-dpdk-integration.conf>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/implementations.json>
  - <https://github.com/litespeedtech/lsquic/releases>
  - <https://github.com/litespeedtech/lsquic/blob/master/CHANGELOG>
  - <https://github.com/litespeedtech/lsquic/security/advisories>
  - <https://github.com/litespeedtech/lsquic/issues?q=CVE>
  - <https://github.com/DPDK/dpdk/blob/v24.11/lib/ethdev/rte_ethdev.h>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/tumi8/lsquic-dpdk`) · [data/wave5/enrich/raw/github_com_tumi8_lsquic_dpdk.json](../../../data/wave5/enrich/raw/github_com_tumi8_lsquic_dpdk.json) (enrichment confidence 0.8)

</details>
