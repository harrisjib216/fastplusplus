# quiche-DPDK (tumi8 kernel-bypass fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C (DPDK kernel-bypass I/O layer added on top of upstream Rust quiche core)` · `no license` · 🟢 active

> DPDK kernel-bypass client/server built on unmodified quiche; 1.83x the single-connection goodput of kernel-socket quiche on 100G NICs.

| | |
|---|---|
| **Beats** | quiche |
| **Claimed result** | Paper Fig. 2 (same-implementation pairs, mean of 50 x 8 GiB HTTP/3 downloads): the quiche-DPDK client+server pair reaches 5937 Mbit/s vs 3241 Mbit/s for upstream quiche (kernel UDP, GSO on, 32x socket buffers), 1.83x as printed in the paper. With SR-IOV (measurement-data/06-dpdk-integration/processed.csv, Fig. 5), quiche-DPDK reaches 6168 Mbit/s (\~1.90x vs 3241, derived from page data). |
| **Workload** | HTTP/3 download of an 8 GiB file between two bare-metal hosts with 100 Gbit/s Intel E810 NICs, using the extended QUIC Interop Runner (framework/config/bypass-paper/01-implementation-matrix.conf). The upstream kernel-socket quiche pair (32x rmem/wmem, NIC offloads on) is compared with the quiche-DPDK pair, 50 repetitions each. |
| **Metric** | throughput |
| **Hardware** | Both hosts: Intel Xeon Gold 6421N (32 cores), 512 GiB DDR5, Intel E810-CQDA2 100 Gbit/s NIC, Debian 12 with Linux 6.1.0-17, DPDK v24.11 (paper Appendix Table I). |
| **Compiler and flags** | tumi8/quiche-dpdk build.sh builds cloudflare/quiche commit c5fc0679 (paper: quiche 0.23.2) with `cargo build --features ffi --release` on the unpinned Rust 'stable' toolchain. It builds the C DPDK client/server with CMAKE_BUILD_TYPE=RelWithDebInfo and DPDK commit 1b3bf112 with meson -Dplatform=generic. The C compiler version is not stated. The kernel quiche baseline is built by a private LRZ GitLab CI, and its flags are unpublished. |
| **Adoption** | 0 stars (research artifact accompanying a NOMS 2026 paper) |
| **Last commit** | 2026-02-12 |
| **Links** | [repository](https://github.com/tumi8/quiche-dpdk) · [benchmark](https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf) |

## Verdict

The test was a single-connection download of an 8 GiB file, 50 repetitions, between two Xeon Gold 6421N hosts with 100G Intel E810 NICs (Debian 12, Linux 6.1, DPDK 24.11). The quiche-DPDK client+server pair averaged 5937 Mbit/s (range 5826-6018). The kernel-socket quiche pair averaged 3241 Mbit/s (range 2554-3605) with GSO on and 32x socket buffers, for 1.83x; on an SR-IOV VF quiche-DPDK reached 6168 Mbit/s. The DPDK side builds quiche 0.23.2 on unpinned Rust stable and C at RelWithDebInfo. The kernel quiche binary comes from a private CI branch ('25.02') whose version and flags are unpublished.

## Use it when

- Bulk single-connection transfers between dedicated bare-metal hosts on 25-100G links, when a quiche-based app is limited by packet I/O and not by crypto (measured: 3.2 -&gt; 5.9 Gbit/s per connection).
- Controlled environments (datacenter point-to-point links, CDN-internal transfers, testbeds) where you can give DPDK a NIC port or an SR-IOV VF plus hugepages and root. The SR-IOV VF run was slightly faster (6168 Mbit/s) and lets the kernel keep the physical port.
- When the downloading side is the bottleneck: a DPDK client against a kernel quiche server alone gave 5464 Mbit/s (1.69x), while a DPDK server with a kernel client gave only 4036 Mbit/s (1.25x).
- As a template for adding DPDK to your own quiche application without patching quiche. The whole integration is about 1,600 lines of C (headers included) around the public quiche C API.
- To reproduce or extend the NOMS 2026 kernel-bypass measurements (configs, CSVs and Zenodo raw data are public).

## Skip it when

- Anything production-facing. It is a single-purpose hq-interop file-transfer demo: no HTTP/3, the client skips certificate verification, the server has a path-traversal hole its own source comment admits, and there is no LICENSE file.
- When you want the most goodput. It is the slowest of the four DPDK stacks in the paper: LSQUIC-DPDK reaches 10756 Mbit/s, picoquic-DPDK 8347 and MsQuic-DPDK 7983, and kernel-socket MsQuic with GSO+GRO reaches 8250 with no bypass at all.
- Shared or general-purpose hosts. One core busy-polls at 100% even when idle, and the programs need hugepages, elevated privileges and a DPDK-bound port or VF. They support IPv4 only, use port 0 with a single RX/TX queue, and do not route: the peer must be ARP-reachable on the same L2 segment.
- Many concurrent connections or multi-core scaling. All work runs on one lcore with one queue and no RSS, and only single-connection transfers were measured.
- Multi-hop or WAN paths. The server disables quiche pacing and sends 32-packet back-to-back bursts; the paper's Appendix D shows DPDK quiche traffic is burstier than kernel quiche.

## How it is fast

It uses a run-to-completion busy-poll loop on one NUMA-local lcore. The loop pulls up to 32 packets with rte_eth_rx_burst, hands each to quiche_conn_recv straight from the mbuf, then drains quiche_conn_send into freshly allocated mbufs and sends them in 32-packet rte_eth_tx_burst batches. This removes the syscalls and kernel/user context switches that the paper identifies as quiche's bottleneck; kernel quiche supports only GSO, which barely helps it (3055 -&gt; 3197 Mbit/s in the paper's data). Other throughput settings are 4096 RX/TX descriptors, hardware IPv4 checksum offload with the UDP checksum zeroed, MBUF_FAST_FREE, CUBIC, and quiche pacing turned off on the server.

## Compared with alternatives

Pick it over LSQUIC-DPDK or picoquic-DPDK only when your stack already uses quiche's API and you want kernel bypass without forking the protocol library. Those siblings patch their libraries and reach about 1.8x and 1.4x higher goodput in the same paper. If you can't dedicate a NIC, a kernel-socket sibling such as ngtcp2 beats quiche without any bypass.

## Integration

| | |
|---|---|
| **Form** | source-drop (two standalone executables, client and server, built with build.sh + CMake; statically links libquiche.a and static DPDK; not a library) |
| **Dependencies** | DPDK at pinned commit 1b3bf112 (v24.11.0; meson/ninja, libnuma, pyelftools); cloudflare/quiche at pinned commit c5fc0679 (release 0.23.2, built with `cargo build --features ffi --release`, cloned with submodules); Rust via rustup; CMake, pkg-config |
| **Minimum toolchain** | C11, CMake 3.20+, Rust 'stable' (unpinned) for quiche 0.23.2, DPDK 24.11 (uses the rte_argparse API). C compiler version not documented. |
| **Platforms** | Linux x86-64 only (build.sh hardcodes x86_64-unknown-linux-gnu; DPDK built with -Dplatform=generic). Tested only on Intel E810 (ice PF driver and iavf VF driver) under Debian 12 / Linux 6.1; other DPDK NICs untested. |
| **Thread safety** | Single-threaded run-to-completion: one worker lcore does RX, quiche processing, TX and rte_timer handling, with no locking. Not designed for multi-threaded use. |
| **Drop-in for the baseline** | partial — the quiche library and its C API are unchanged, but the application must replace all socket I/O, event-loop, ARP and IP/UDP header code with DPDK code as this repo does. It replaces quiche's example socket apps, not quiche itself. |

## Gotchas

- The protocol is hq-interop/HTTP/0.9, not HTTP/3: ALPN is `hq-interop`/`http/0.9` and the request is a bare `GET /path\r\n`. The server reads the whole requested file into one malloc'd buffer before sending, so an 8 GiB file costs 8 GiB of RAM.
- Possible memory bugs from reading the code: TX-path rte_pktmbuf_alloc results are never NULL-checked. An ARP frame for another IP, or a malformed one, is freed in handle_arp_request and then again by rte_pktmbuf_free_bulk, which is a double free. This is harmless on the paper's point-to-point fiber but risky on a shared L2 or SR-IOV segment that carries broadcast ARP.
- Interop is flaky in the published data. With the quiche-DPDK server, 7 of 50 runs against the picoquic client and 6 of 50 against the picoquic-DPDK client recorded no goodput (implementation-matrix processed.csv).
- The AF_XDP-style 'quiche-dpdkxdp' variant in the SR-IOV dataset averaged only 3168 Mbit/s and was bimodal (median 1596). That is no better than kernel quiche. Its xdp branch is not on GitHub; only main and an instrumented perf branch are.

## Known shortcomings

- Research kernel-bypass client/server around an unmodified quiche; no licence (reference only). Needs DPDK and dedicated NICs; baseline builds are private and compiler versions not pinned.
- Not HTTP/3: it negotiates only hq-interop/http/0.9 and sends a bare GET. Frozen paper artifact (3 commits, no LICENSE file). Source defects: path traversal in the server (admitted in a comment), whole file loaded into one malloc, client disables certificate verification, TX mbuf allocations not NULL-checked, ARP frames for other IPs freed twice; IPv4 only, one port/queue/lcore. With a quiche-DPDK server, 13 of 100 picoquic(-DPDK) client runs produced no goodput. An unpublished XDP variant averaged 3168 Mbit/s, no gain over kernel quiche. Slowest of the four DPDK stacks; kernel MsQuic with GSO/GRO (8250 Mbit/s) beats it without bypass.

## Caveats and trade-offs

Peer-reviewed and published: NOMS 2026, Rome, pp. 1-8, DOI 10.1109/NOMS69089.2026.11668379. The open preprint is on net.in.tum.de, and the dataset is Zenodo 10.5281/zenodo.18630971. The earlier 'DOI TODO / unpublished' note is outdated. This is not a GitHub fork of quiche. It is a small standalone C client/server (about 50 KB of C) that replaces quiche's mio-based example apps with a DPDK busy-polling loop and links the unmodified upstream quiche library through its FFI. The paper states that no quiche library code changed. The comparison pits kernel bypass (a DPDK-bound NIC port or SR-IOV VF, one polling thread) against kernel UDP sockets. quiche-DPDK is the slowest of the four DPDK stacks (LSQUIC-DPDK reaches 10756 Mbit/s) and is below upstream MsQuic with GSO+GRO (8250 Mbit/s). There is no LICENSE file.

DPDK requires dedicating a whole NIC/queue to userspace polling (no shared use with the kernel network stack), hugepages, and root/elevated privileges; adds substantial deployment complexity vs a drop-in library. No license file found in this repo (upstream quiche is Apache-2.0/BSD-2-Clause), so treat the fork's own additions as 'look but don't copy' pending clarification from the authors.

## Maintenance

A frozen research artifact: 3 commits, last push 2026-02-12 to accompany the NOMS 2026 paper, 0 stars, no issues. There is no LICENSE file (upstream quiche is BSD-2-Clause), so read it as a reference design and don't vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NOMS 2026 paper (DOI 10.1109/NOMS69089.2026.11668379). Its Fig. 2 prints quiche-DPDK pair 5937 Mbit/s (1.83x) vs upstream quiche pair 3241 Mbit/s, and the means match measurement-data/01-implementation-matrix/processed.csv (n=50 each). The code, configs and CPU (Xeon Gold 6421N) are public. It is not A: Rust/GCC versions are not stated (unpinned 'stable'), and the kernel quiche baseline binary comes from a private GitLab CI with unpublished flags.
- **Verifier notes:** The numbers are confirmed and printed directly in paper Fig. 2, so they are not only derived from the CSV. The paper is now published, and the hardware is filled in from Table I. I set is_fork_of to null because GitHub reports fork=false and the repo is a wrapper app around unmodified quiche. The license is still none, so usability stays 'reference', and last_commit 2026-02-12 is verified.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/01-implementation-matrix/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/06-dpdk-integration/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/README.md>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/config/bypass-paper/01-implementation-matrix.conf>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/testbed/testbed_stoi-pact.json>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/implementations.json>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/fetch_artifacts.py>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/quiche-dpdk/build.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/evaluation/paper-plots.ipynb>
  - <https://github.com/tumi8/quiche-dpdk>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/README.md>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/build.sh>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/CMakeLists.txt>
  - <https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf>
  - <https://www.net.in.tum.de/publications/>
  - <https://api.crossref.org/works/10.1109/noms69089.2026.11668379>
  - <https://zenodo.org/api/records/18630971>
- **Sources the enricher read:**
  - <https://github.com/tumi8/quiche-dpdk>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/README.md>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/build.sh>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/CMakeLists.txt>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/.gitignore>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/include/dpdk.h>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/include/quic_common.h>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/include/arp.h>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/include/args_client.h>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/include/args_server.h>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/dpdk.c>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/quic_common.c>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/server.c>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/client.c>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/arp.c>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/args_server.c>
  - <https://github.com/tumi8/quiche-dpdk/blob/main/src/args_client.c>
  - <https://github.com/tumi8/quiche-dpdk/commits/main>
  - <https://github.com/tumi8/quiche-dpdk/branches>
  - <https://github.com/tumi8/quiche-dpdk/compare/main...perf>
  - <https://github.com/tumi8/quiche-dpdk/issues>
  - <https://www.net.in.tum.de/fileadmin/bibtex/publications/papers/spaethj-noms2026.pdf>
  - <https://github.com/tumi8/quic-bypass-paper>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/README.md>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/config/bypass-paper/01-implementation-matrix.conf>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/implementations.json>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/framework/testcases.py>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/quiche-dpdk/build.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/quiche-dpdk/run-server.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/quiche-dpdk/run-client.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/quic-dpdk-implementations/quiche-dpdk/setup-env.sh>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/01-implementation-matrix/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/02a-no-offloading/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/02b-only-gso/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/02c-only-gro/processed.csv>
  - <https://github.com/tumi8/quic-bypass-paper/blob/main/measurement-data/06-dpdk-integration/processed.csv>
  - <https://github.com/DPDK/dpdk/commit/1b3bf1128d9bda5595861814792f74b8f57160c8>
  - <https://github.com/cloudflare/quiche/commit/c5fc0679ece63636a2264ef273c75f08a405fdf7>
  - <https://github.com/cloudflare/quiche>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/tumi8/quiche-dpdk`) · [data/wave5/enrich/raw/github_com_tumi8_quiche_dpdk.json](../../../data/wave5/enrich/raw/github_com_tumi8_quiche_dpdk.json) (enrichment confidence 0.85)

</details>
