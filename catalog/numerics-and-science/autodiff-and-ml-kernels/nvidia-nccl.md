# NCCL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 for most of the project; some parts keep a BSD-3-Clause license (LICENSE.txt)` · 🟢 active

> NVIDIA's GPU collective-communication library (all-reduce, all-gather, send/recv); far faster than Gloo for large GPU all-reduces, slower for small ones.

| | |
|---|---|
| **Beats** | Gloo CPU allreduce_ring (gloo/benchmark/main.cc CPU benchmark, run with -s 2), compared against NCCL on GPUs |
| **Claimed result** | gloo issue #158 (Dec 26 2018, user report; NCCL 2.3.7 vs Gloo commit 1d9e62a, 5000 iterations). IB RDMA 100 Gbps: NCCL faster only from 64 KB up: 64 KB 0.13 ms vs 0.155 ms, 128 KB 0.09 ms vs 1.073 ms, 256 KB 0.13 ms vs 20.161 ms (largest size in that table); Gloo faster from 1 KB to 32 KB (1 KB 0.039 ms vs NCCL 0.16 ms; 32 KB 0.088 ms vs 0.15 ms). TCP/IP sockets: NCCL faster from 128 KB up: 128 KB 3.66 ms vs 5.614 ms, 256 KB 6.25 vs 10.980, 512 KB 7.12 vs 20.544, 1 MB 11.91 vs 39.855, 2 MB 20.9 vs 78.237; Gloo faster from 1 KB to 64 KB (1 KB 0.354 ms vs NCCL 1.89 ms; 64 KB 3.813 ms vs 4.02 ms). Largest ratio about 155x at 256 KB on IB, 3.7x at 2 MB on TCP (derived from page data). |
| **Workload** | Allreduce latency by message size (1 KB to 256 KB on IB RDMA, 1 KB to 2 MB on TCP/IP) between two servers with 8 NVIDIA V100 GPUs each, NCCL 2.3.7 versus Gloo commit 1d9e62a running its CPU-buffer allreduce_ring benchmark with -s 2 and 5000 iterations (user-posted GitHub issue; NCCL-side command not shown). |
| **Metric** | latency |
| **Hardware** | Two Ubuntu servers with 8 V100 GPUs each; 100 Gbps IB RDMA (test 1) or TCP/IP sockets (test 2); CPU model not stated |
| **Adoption** | 5.1k stars, 1.4k forks |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/NVIDIA/nccl) · [benchmark](https://github.com/facebookincubator/gloo/issues/158) |

## Verdict

One user's report filed against Gloo (issue #158, Dec 2018): NCCL 2.3.7 on two 8x V100 servers against Gloo commit 1d9e62a's CPU allreduce_ring with 2 processes and 5000 iterations. NCCL loses below 64 KB (IB) or 128 KB (TCP) and wins above, up to 0.13 ms vs 20.161 ms at 256 KB on IB and 20.9 ms vs 78.237 ms at 2 MB on TCP. No compiler, CPU model, NCCL command or latency statistic is given, and the shown Gloo command cannot produce most of the table's sizes. PyTorch's docs separately state that Gloo runs slower than NCCL on GPUs, without numbers.

## Use it when

- Data-parallel or tensor-parallel training on NVIDIA GPUs: gradient all-reduce and parameter all-gather of tens of KB to GBs per call, where the record's data show NCCL ahead of Gloo from 64 KB (IB) or 128 KB (TCP) upward.
- Multi-GPU nodes with NVLink or NVSwitch (DGX/HGX class), where NVLS and NVLink peer paths are available that host-memory libraries cannot use.
- Multi-node GPU clusters on InfiniBand or RoCE with GPUDirect RDMA; PyTorch's own docs say to use NCCL on GPU hosts with InfiniBand because it is the only backend there that supports InfiniBand and GPUDirect.
- Code that already orders work on CUDA streams and wants communication to overlap compute without a host round trip (stream-ordered API, CUDA graph capture is supported by nccl-tests -G).

## Skip it when

- Small messages where latency dominates: in the only measured comparison Gloo was faster at every size up to 32 KB on IB (1 KB: 0.039 ms vs NCCL 0.16 ms) and up to 64 KB on TCP (1 KB: 0.354 ms vs 1.89 ms).
- CPU tensors or hosts without NVIDIA GPUs: NCCL needs CUDA and GPU buffers; PyTorch's rule of thumb is Gloo for CPU training.
- Non-NVIDIA accelerators (AMD, Intel XPU): use the vendor's fork or library instead (PyTorch docs point XPU to XCCL).
- Applications that cannot guarantee every rank issues the same collectives in the same order: a mismatch hangs all ranks, and hangs dominate the issue tracker (for example #257 'AllReduce hangs', #1184 'all_reduce_perf hangs on DGX-H100', #1013 ncclCommAbort stuck).
- Windows or WSL deployments: issue #442 'NCCL tests don't work on WSL'; the build and packaging target Linux (deb, rpm, txz).

## How it is fast

Collectives run as CUDA kernels that move and reduce data GPU-to-GPU over NVLink/NVSwitch/PCIe peer access and GPUDirect RDMA on InfiniBand, so data never stages through host memory. A per-call tuner picks among seven algorithms (Ring, Tree, CollNetDirect, CollNetChain, NVLS, NVLSTree, PAT in src/init.cc), with NVLS and CollNet offloading reductions to NVLink SHARP or in-network SHARP switches. Three wire protocols trade latency for bandwidth: LL interleaves a 4-byte flag with every 4 bytes of data so receivers poll memory instead of synchronizing, LL128 uses one 8-byte flag per 128-byte line, and Simple uses large chunks with explicit fences (src/include/device.h).

## Compared with alternatives

None of the siblings does inter-GPU communication; NCCL is the collective layer under multi-GPU training in PyTorch, MXNet and Flashlight, so pick it when gradients or activations must cross GPUs. The kernel siblings (FlashAttention, fast.cu, BitBLAS) speed up compute on one GPU.

## Integration

| | |
|---|---|
| **Form** | shared lib (libnccl.so) or static lib (libnccl_static.a); prebuilt packages from NVIDIA, or built with make src.build; Python wheel target |
| **Dependencies** | CUDA toolkit and driver; NVIDIA GPU; optional InfiniBand verbs / GPUDirect RDMA stack and external network plugins (libnccl-net.so); MPI only for multi-process nccl-tests |
| **Minimum toolchain** | nvcc plus a host C++ compiler at C++14 (C++17 when building with CUDA 13, per makefiles/common.mk); default gencode starts at sm_60 for CUDA 11/12 and sm_75 for CUDA 13; exact minimum CUDA version not documented in the README |
| **Platforms** | Linux on NVIDIA GPUs (Pascal sm_60 through Blackwell sm_100/sm_120 and later in the default gencode list); interconnects PCIe, NVLink, NVSwitch, InfiniBand verbs, TCP sockets |
| **Thread safety** | Collective calls on a communicator may synchronize across CPUs, so nccl.h requires each rank's calls from a different thread or process, or wrapped in ncclGroupStart/ncclGroupEnd; ncclCommInitRank blocks until all ranks join. |
| **Drop-in for the baseline** | partial — frameworks swap it in as a backend (PyTorch backend='nccl' instead of 'gloo'), but the raw API differs from Gloo's and requires GPU-resident buffers and CUDA streams |

## Gotchas

- Harness flaw behind the record's numbers (gloo issue #158): the Gloo command shown passes no --elements, and at the reported Gloo commit 1d9e62a gloo/benchmark/runner.cc sweeps 100 to 5,000,000 floats in 1-2-5 steps (400 B, 800 B, 2,000 B, 4,000 B, 8,000 B, 20,000 B, 40,000 B, 80,000 B, 200,000 B ...), so most of the table's power-of-two rows (1 KB, 16 KB, 32 KB, 64 KB, 128 KB, 256 KB, 512 KB, 1 MB) cannot have come from the command as shown. The report also never says which Gloo column (min, p50, p99 or max) was copied, how many NCCL ranks or GPUs ran, or which NCCL tool was used, and the issue has no replies.
- The baseline is not like-for-like: allreduce_ring is Gloo's CPU host-memory benchmark with 2 processes (-s 2), not its CUDA variant. Gloo's own README says its CUDA-aware algorithms depend on NCCL, so on GPUs Gloo is partly NCCL underneath.
- The NCCL column is noisy and both TCP columns are slow: 1 KB 0.16 ms vs 2 KB 0.06 ms, and 128 KB (0.09 ms) is faster than 64 KB (0.13 ms) on IB. The reporter flagged possible stragglers. On TCP, NCCL's 2 MB in 20.9 ms is about 100 MB/s, roughly a 1 Gbit/s link (derived from page data), so the TCP rows say little about modern Ethernet.
- Each call enqueues a kernel and returns at once. Errors and hangs surface asynchronously (ncclCommGetAsyncError, ncclCommAbort), and issue #750 reports a hang on all ranks under CUDA_LAUNCH_BLOCKING=1 since v2.13. Communication kernels also take SMs from compute; ncclConfig_t exposes minCTAs/maxCTAs to cap them.

## Known shortcomings

- Gloo issue #158 user report (2018): Gloo is faster up to 32 KB on InfiniBand and up to 64 KB on TCP; Gloo ran a CPU allreduce_ring with -s 2 against GPU NCCL and the NCCL command is not shown. Apache-2.0 with BSD-3-Clause parts. Filed under numerics-and-science/autodiff-and-ml-kernels.
- Enricher: the Gloo command shown in issue #158 has no --elements and the runner at that commit sweeps 100 to 5,000,000 floats in 1-2-5 steps, so the table's 1 KB to 1 MB rows cannot come from the command as shown; the Gloo latency statistic (min/p50/p99/max), NCCL rank count and NCCL tool are unstated and the issue has zero replies. The NCCL column is noisy (IB 1 KB 0.16 ms vs 2 KB 0.06 ms; 128 KB faster than 64 KB) and the TCP rows imply roughly a 1 Gbit/s link. Gloo's CUDA algorithms depend on NCCL, so the GPU baseline is not independent.

## Caveats and trade-offs

Weak, apples-to-oranges evidence for such a notable project: the only reachable numbers are one user's report filed against Gloo (reporter: 'gloo has poor performance for large size all-reduce'). The Gloo command is './benchmark ... -s 2 ... allreduce_ring', and allreduce_ring is the CPU-memory algorithm in gloo/benchmark/main.cc (the GPU variants are cuda_allreduce_\* in cuda_main.cc), so Gloo ran on host buffers with 2 processes while the NCCL command, buffer placement and rank count are not shown. Gloo's 20.161 ms at 256 KB on IB looks like a Gloo ibverbs pathology rather than a representative baseline. NCCL lost at every size up to 32 KB on IB and up to 64 KB on TCP. Versions are from 2018 (NCCL 2.3.7). The repository README and nccl-tests carry no baseline numbers. Published studies (OSU MVAPICH2-GDR papers, arXiv 1707.09414 and 1810.11112, snippet only since arXiv is blocked) report MVAPICH2-GDR beating NCCL for small messages (up to 17x for 8-byte allreduce per snippet), so NCCL is not uniformly faster than MPI. No CPU model, compiler or flags. Category and domain are a best fit (GPU collective communication has no dedicated category).

GPU-only collectives (all-reduce, all-gather, reduce, broadcast, reduce-scatter, send/recv) over PCIe, NVLink, NVSwitch, InfiniBand verbs and TCP sockets; NVIDIA GPUs and CUDA required; mostly Apache-2.0 with BSD parts (LICENSE.txt), although the README still carries an 'all rights reserved' 2015-2020 notice.

## Maintenance

Very active: NCCL 2.32.3 was merged to master on 2026-09-17, with frequent releases. Apache-2.0 per the SPDX headers and LICENSE.txt, with some files under BSD-3-Clause (the README's 'all rights reserved' line is stale). Usable as-is, but the catalogue evidence is weak (tier C, one 2018 user report with harness gaps), not a reproducible benchmark.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** The only numbers are one user's tables in gloo issue #158 (Gloo benchmark command shown, NCCL command, buffer placement and process count not shown, no CPU model or compiler); not a peer-reviewed or recognized third-party suite and not reproducible, so C at best. Kept at C, but the claim was overstated: NCCL loses at every size up to 32 KB on IB and up to 64 KB on TCP, not only at 1 KB.
- **Verifier notes:** Numbers verified on gloo issue #158 but the record understated Gloo's wins (Gloo faster 1-32 KB on IB, 1-64 KB on TCP) and missed that Gloo ran its CPU allreduce_ring with 2 processes against GPU NCCL; tier stays C, claim corrected. License is Apache-2.0 with BSD-3-Clause parts; metadata (5.1k stars, 1.4k forks, last commit 2026-09-17, active) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `license`, `caveats`
- **Shortcomings recorded by:** third-party issue (verifier downgrade, claim narrowed); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/facebookincubator/gloo/issues/158>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/main/gloo/benchmark/main.cc>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/main/gloo/benchmark/cuda_main.cc>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/LICENSE.txt>
  - <https://github.com/NVIDIA/nccl>
  - <https://github.com/NVIDIA/nccl/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/makefiles/common.mk>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/makefiles/version.mk>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/src/nccl.h.in>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/init.cc>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/include/device.h>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/include/nccl_common.h>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/tuning/tuning.cc>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/collectives.cc>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/device/prims_ll.h>
  - <https://raw.githubusercontent.com/NVIDIA/nccl/master/src/device/prims_ll128.h>
  - <https://raw.githubusercontent.com/NVIDIA/nccl-tests/HEAD/README.md>
  - <https://github.com/NVIDIA/nccl>
  - <https://github.com/NVIDIA/nccl/tree/master/src>
  - <https://github.com/NVIDIA/nccl/commits/master>
  - <https://github.com/NVIDIA/nccl/issues?q=is%3Aissue+hang+sort%3Acomments-desc>
  - <https://github.com/NVIDIA/nccl/issues/750>
  - <https://github.com/facebookincubator/gloo/issues/158>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/main/README.md>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/main/gloo/benchmark/main.cc>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/main/gloo/benchmark/options.cc>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/main/gloo/benchmark/runner.cc>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/1d9e62a/gloo/benchmark/runner.cc>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/1d9e62a/gloo/benchmark/options.cc>
  - <https://raw.githubusercontent.com/facebookincubator/gloo/1d9e62a/gloo/benchmark/main.cc>
  - <https://raw.githubusercontent.com/pytorch/pytorch/main/docs/source/distributed.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/nvidia/nccl`) · [data/wave11/enrich/raw/github_com_nvidia_nccl.json](../../../data/wave11/enrich/raw/github_com_nvidia_nccl.json) (enrichment confidence 0.6)

</details>
