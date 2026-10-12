# eRPC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Kernel-bypass C++ datacenter RPC library over DPDK UDP or InfiniBand, near FaSST/RDMA speed on lossy Ethernet.

| | |
|---|---|
| **Beats** | NSDI'19 paper baselines: FaSST RPCs and raw RDMA reads/writes (measured; eRPC is comparable but slightly slower), IX (per-core RPC rate quoted from the IX paper), NetChain and ZabFPGA replication (their published numbers), and the Cell RDMA B-tree (published numbers). The paper never benchmarks kernel TCP/UDP socket RPC or HERD. |
| **Claimed result** | NSDI'19 paper: one core handles \~10M small RPCs/s vs \~1.5M 64 B RPCs/s with IX (IX figure quoted, not re-measured; \~6.7x derived from page data). 3-way Raft replication takes 5.5 us median vs NetChain's published 9.7 us (\~1.8x, derived from page data) and is 3% slower than ZabFPGA at the leader (3.1 vs 3.0 us). Masstree-over-eRPC median GET is 2.7 us, 'around 10x faster' than Cell's RDMA B-tree. Against its measured RDMA baselines eRPC is slightly slower: per-thread small-RPC rate up to 18% below FaSST, median latency up to 800 ns above RDMA reads, and at least 70% of RDMA-write bandwidth for requests of 32 kB or more (75 Gbps peak on one core). The README's absolute figures (2.3 us RTT, \~10M RPCs/s per core, 60-80M RPCs/s per NIC, 75 Gbps, 5.3 us Raft) have no baseline on that page. The paper gives 5.5 us, not 5.3 us, for Raft and does not contain the 60-80M per NIC figure. |
| **Workload** | Small (32-byte) and large (8MB) RPC calls over Ethernet/InfiniBand/RoCE NICs, plus a 3-way Raft replication port, on commodity DPDK-capable or Mellanox NICs |
| **Metric** | throughput |
| **Hardware** | NSDI'19 Table 1 lists three clusters. CX3: 11 nodes, 56 Gbps ConnectX-3 InfiniBand, Intel Xeon E5-2650 (8 cores). CX4: 100 CloudLab nodes, 25 GbE ConnectX-4 Lx lossy Ethernet, Xeon E5-2640 v4 (10 cores). CX5: 8 nodes, dual-port 40 GbE ConnectX-5, Xeon E5-2697 v3 (14 cores) or E5-2683 v4 (16 cores). Large-RPC bandwidth was measured between two CX5 nodes over 100 Gbps ConnectX-5 InfiniBand. |
| **Compiler and flags** | The paper does not state them. The repo's CMakeLists.txt with the default PERF=ON uses CMAKE_BUILD_TYPE RelWithDebInfo plus -std=c++11 -march=native. The compiler is not named. |
| **Adoption** | 907 stars |
| **Last commit** | 2024-05-09 |
| **Links** | [repository](https://github.com/erpc-io/eRPC) · [benchmark](https://www.usenix.org/system/files/nsdi19-kalia.pdf) |

## Verdict

In the NSDI'19 paper, one thread per node on 11 CloudLab CX4 nodes (25 GbE ConnectX-4 Lx, Xeon E5-2640 v4), with 32 B RPCs, batch size 3 and congestion control on, issued 4.96 Mrps and served as many, so about 10M RPCs/s per core. That is up to 18% below FaSST's numbers from the same CX3 InfiniBand cluster. Median latency was 2.3 µs against 2.0 µs for RDMA reads on CX5. The larger wins are comparisons across papers on different hardware, never re-measured: about 6.7x IX's published 1.5M 64 B RPCs/s, Raft at 5.5 µs against NetChain's published 9.7 µs, and roughly 10x lower GET latency than Cell. The paper names no compiler; the repo builds RelWithDebInfo with -march=native and -flto.

## Use it when

- Service-to-service or storage RPC where you own both ends and run on bare-metal Mellanox CX3–CX5 or other DPDK-capable 10 GbE+ NICs, and you want a few microseconds of median latency (paper: 2.3 µs on 40 GbE CX5, 3.7 µs on 25 GbE CX4)
- Small, fixed-size requests (32 B class) at high rate: in the paper one core handles \~10M RPCs/s when it is both client and server in an all-to-all cluster of about 10 or more nodes
- Replication or key-value work that would otherwise need RDMA or PFC: the paper runs a stock Raft port at 5.5 µs 3-way replication and Masstree at 2.7 µs median GET on lossy Ethernet
- Bulk transfers up to 8 MB per message on a fast link: up to 75 Gbps on one core over 100 Gbps InfiniBand (raise the 1024 B DPDK MTU constant for bandwidth on Ethernet)
- Research baselines where you need a general RPC layer within \~18% of FaSST's small-RPC rate and within 800 ns of RDMA-read latency

## Skip it when

- Anything that must speak HTTP or TLS, or talk to clients that are not eRPC: the UDP/IB wire protocol is custom, so it does not replace any of the HTTP servers in this category
- Public-cloud VMs, containers, dev laptops, or setups without root: it needs hugepages (at least 1024 per NUMA node), DPDK owning the NIC port or ibverbs, and NIC flow steering. Only Azure accelerated networking is documented, and the author notes that cloud guests often lack flow steering (issue #44)
- Low-rate or bursty callers that sleep between RPCs: latency grows with idle time (issues #104/#116), and the fix PR #123 is still unmerged
- Non-x86 hosts: timing uses the rdtsc instruction via inline asm and the build uses -march=native. An aarch64 port needs patches and trips the TSC-frequency assert (issue #111, open)
- Long-lived production dependencies: the last commit was 2024-05-09 and the authors now point new users to microsoft/machnet. Networks with more than \~0.01% loss or with packet reordering also hurt it: reordered packets are dropped and handled with go-back-N and a 5 ms RTO, and 8 MB throughput falls to 18 Gbps at 1e-4 loss

## How it is fast

Each user thread polls its own NIC queue from userspace and runs short handlers to completion inside the event loop. Longer handlers can go to up to 8 eRPC background threads. The paper's common-case optimizations are zero-copy, single-DMA msgbufs (packet 1's header sits before the data and later headers go at the end), request handlers that read directly from the RX ring, preallocated MTU-sized responses, multi-packet RQ, and unsignaled, batched TX. The wire protocol is client-driven: a session's packet credits are capped near one bandwidth-delay product, and eRPC relies on large dynamic switch buffers so that loss stays rare. Congestion control is Timely plus a Carousel-style timing-wheel rate limiter. When a session is uncongested it skips the Timely update and the wheel and reads rdtsc once per batch, which cuts congestion-control overhead from 20% to 9%. The transports are picked at compile time through a template parameter (static polymorphism), so there are no virtual calls.

## Compared with alternatives

Pick eRPC over Demikernel, Shenango, or FlexTOE when both ends are your own C++ code and you want finished RPC semantics (at-most-once execution, loss recovery, congestion control, nested and background handlers) at millions of small RPCs per core. Pick those siblings when you need a TCP or sockets-style path that other software can talk to, such as Demikernel's DPDK TCP stack or Shenango serving memcached. The HTTP servers here (Drogon, H2O, Lwan, Crow) solve a different problem and are not alternatives.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | DPDK 21.11 (dpdk transport; README says other versions are unsupported) or rdma-core/ibverbs (infiniband/RoCE transport); libnuma, pthread, rt; bundled gflags, HdrHistogram_c, googletest and asio headers; 2 MB hugepages; optional libpmem for some apps |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11), CMake with pkg-config for DPDK; author reports GCC 7.4 works (issue #33); builds with -Wall -Wextra -Werror -pedantic, so newer compilers may fail (issue #65 open) |
| **Platforms** | Linux x86-64 only in practice (rdtsc inline asm, -march=native); NICs: Mellanox CX3–CX5 tested, any DPDK NIC with flow steering, Azure DPDK VMs; a WIN32 DPDK path exists in CMakeLists but is not documented; aarch64 unsupported |
| **Thread safety** | One Rpc endpoint per user thread. rpc.h says none of the Rpc functions are thread-safe for user threads, and session and event-loop calls must come from the creating thread. Only eRPC's own background threads may call alloc/enqueue_request/enqueue_response. There is one Nexus per process (multiple Nexus in one process is open issue #84). |
| **Drop-in for the baseline** | no |

## Gotchas

- Idle gaps inflate latency. TimingWheel::reap() advances one slot at a time with no fast-forward, and enqueue_request stamps a stale event-loop TSC, so a request after more than 5 ms idle is falsely retransmitted. The workaround is to keep calling run_event_loop_once() instead of sleeping. The fix is PR #123, open since 2026-08-06.
- Most tuning is compile-time. kSessionReqWindow = 8 outstanding requests per session, kSessionCredits = 32, kNumRxRingEntries = 4096 (so about 128 sessions per Rpc before create_session returns -ENOMEM), kRpcRTOUs = 5000, and kMTU = 1024 B on DPDK. Two-machine tests do not reach the 10M RPC/s figure (issue #35: \~1.5 Mrps; issue #121: 3.1 vs 5 Mrps on 10 xl170 nodes).
- Buffer ownership is strict. With kZeroCopyRX, a single-packet request buffer is valid only during the handler. A response must use the ReqHandle's pre_resp_msgbuf_ or dyn_resp_msgbuf_, not your own buffer, and eRPC owns request and response msgbufs until the continuation runs. Message size is capped at 8 MB.
- Session setup goes over kernel UDP on the management network (ports 31850+n, reachable by hostname), not over the DPDK port. By default only one process can use a DPDK port; the multi-process daemon has been seen stuck in rte_eth_tx_burst (#118). The Nexus segfaults when CPUs are offline, for example with HT disabled (#31; the fix PR #36 has been open since 2019).

## Known shortcomings

- Never benchmarked against kernel TCP/UDP RPC or gRPC; against FaSST and raw RDMA it is slightly slower (up to 18% lower per-thread rate, up to 800 ns more latency). Its wins over IX, NetChain and Cell use those papers' published numbers. Needs DPDK/RDMA NICs. Stale since 2024-05.
- Idle-latency bug: after more than 5 ms idle, requests are falsely retransmitted (timing-wheel reap walks slot by slot, stale timestamp in enqueue_request; #104, #116); fix PR #123 unmerged, workaround is to keep polling. \~10M RPC/s per core needs \~10 nodes all-to-all (8 outstanding per session); users saw 1.5 Mrps on two machines (#35) and 3.1 vs 5 Mrps on 10 nodes (#121). Compile-time limits: \~128 sessions per Rpc endpoint by default, DPDK MTU hard-coded 1024 B. x86-64 Linux only (rdtsc, -march=native; aarch64 #111), needs hugepages/root/DPDK 21.11 or rdma-core; Nexus segfaults with offline CPUs (#31). Go-back-N with 5 ms RTO: usable only up to \~0.01% loss. Not an HTTP server (no HTTP/TLS). Faster claims compare against numbers from other papers; up to 18% slower per thread than FaSST. Last commit 2024-05; authors point to microsoft/machnet.

## Caveats and trade-offs

The paper's thesis is that eRPC is comparable to specialized systems while staying general. It never measures kernel TCP/UDP socket RPC or HERD, and against FaSST and raw RDMA it is slightly slower. Its 'faster' comparisons (IX, NetChain, Cell, and FaRM at scale) use numbers from other papers on different hardware; the authors say the NetChain comparison 'must be taken with a grain of salt'. The category fit is datacenter RPC over DPDK/RDMA rather than HTTP serving. The README's 5.3 us Raft and 60-80M RPCs/s per NIC figures are not in the paper, which gives 5.5 us. Authors now point new users to microsoft/machnet. The LICENSE file is the Apache-2.0 notice header (GitHub reports NOASSERTION).

Requires DPDK/RDMA-capable NICs and huge pages; a binary RPC library, not an HTTP-semantics server (no TLS/HTTP parsing); app must integrate its session/event-loop model

## Maintenance

Stale since the last commit on 2024-05-09 (last release v0.2, 2021), with 19 open issues and 5 open PRs, including the unmerged idle-latency fix. The authors point new users to microsoft/machnet. It is Apache-2.0 (per LICENSE and README; GitHub shows NOASSERTION) and about 6,200 lines of C++ per the paper, so it can be vendored, but expect to own DPDK and rdma-core version pinning yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The README at benchmark_url lists only absolute figures with no baseline. The linked peer-reviewed NSDI'19 paper does make comparative claims, but mostly against numbers published in other papers: \~10M vs \~1.5M 64 B RPCs/s per core against IX (quoted), 5.5 vs 9.7 us Raft replication against NetChain (published), and \~10x lower GET latency than Cell. The benchmark code (apps/small_rpc_tput, apps/large_rpc_tput, apps/latency, apps/smr) runs only eRPC, and the compiler is never named, so it cannot be A. Tier B is kept, but the win comes from comparisons across papers.
- **Verifier notes:** Metadata checked with gh: Apache-2.0 per the LICENSE file, not archived, not a fork, 907 stars, last commit 2024-05-09, so stale is correct. Tier stays B, but the verdict is downgrade because the record's baseline (kernel TCP/UDP RPC, FaSST/HERD) misstates the paper: it never benchmarks kernel sockets or HERD, and eRPC loses slightly to FaSST.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/erpc-io/eRPC#readme>
  - <https://github.com/erpc-io/eRPC>
  - <https://github.com/erpc-io/eRPC/blob/master/LICENSE>
  - <https://github.com/erpc-io/eRPC/blob/master/CMakeLists.txt>
  - <https://github.com/erpc-io/eRPC/tree/master/apps>
  - <https://www.usenix.org/system/files/nsdi19-kalia.pdf>
- **Sources the enricher read:**
  - <https://github.com/erpc-io/eRPC>
  - <https://github.com/erpc-io/eRPC#readme>
  - <https://github.com/erpc-io/eRPC/blob/master/CMakeLists.txt>
  - <https://github.com/erpc-io/eRPC/blob/master/LICENSE>
  - <https://github.com/erpc-io/eRPC/blob/master/src/rpc.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/nexus.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/tweakme.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/rpc_types.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/rpc_constants.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/common.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/sm_types.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/pkthdr.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/transport.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/transport_impl/dpdk/dpdk_transport.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/transport_impl/infiniband/ib_transport.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/util/timer.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/util/huge_alloc.h>
  - <https://github.com/erpc-io/eRPC/blob/master/src/rpc_impl/rpc_sm_api.cc>
  - <https://github.com/erpc-io/eRPC/blob/master/hello_world/server.cc>
  - <https://github.com/erpc-io/eRPC/blob/master/hello_world/client.cc>
  - <https://github.com/erpc-io/eRPC/blob/master/hello_world/common.h>
  - <https://github.com/erpc-io/eRPC/blob/master/hello_world/Makefile>
  - <https://github.com/erpc-io/eRPC/issues>
  - <https://github.com/erpc-io/eRPC/pulls>
  - <https://github.com/erpc-io/eRPC/issues/20>
  - <https://github.com/erpc-io/eRPC/issues/31>
  - <https://github.com/erpc-io/eRPC/issues/33>
  - <https://github.com/erpc-io/eRPC/issues/35>
  - <https://github.com/erpc-io/eRPC/issues/44>
  - <https://github.com/erpc-io/eRPC/issues/100>
  - <https://github.com/erpc-io/eRPC/issues/104>
  - <https://github.com/erpc-io/eRPC/issues/111>
  - <https://github.com/erpc-io/eRPC/issues/113>
  - <https://github.com/erpc-io/eRPC/issues/115>
  - <https://github.com/erpc-io/eRPC/issues/116>
  - <https://github.com/erpc-io/eRPC/issues/118>
  - <https://github.com/erpc-io/eRPC/issues/121>
  - <https://github.com/erpc-io/eRPC/pull/123>
  - <https://www.usenix.org/system/files/nsdi19-kalia.pdf>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/erpc-io/erpc`) · [data/wave5/enrich/raw/github_com_erpc_io_erpc.json](../../../data/wave5/enrich/raw/github_com_erpc_io_erpc.json) (enrichment confidence 0.85)

</details>
