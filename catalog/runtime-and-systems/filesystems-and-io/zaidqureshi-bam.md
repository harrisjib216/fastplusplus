# BaM (Big accelerator Memory)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> CUDA library and kernel driver that let GPU threads issue NVMe reads and writes themselves, bypassing CPU-orchestrated storage paths.

| | |
|---|---|
| **Beats** | CPU-orchestrated GPU storage access (cudaMemcpy over POSIX I/O / GPUDirect Storage) |
| **Claimed result** | README (ASPLOS'23 abstract): 1.0x (BFS) and 1.49x (CC) end-to-end speedup for graph analytics while reducing hardware cost by up to 21.7x; 5.3x speedup on data-analytics workloads on the same hardware. |
| **Workload** | GPU threads submit NVMe queue requests directly with a software cache, BFS and CC graph analytics, data analytics queries |
| **Metric** | throughput |
| **Adoption** | 244 stars |
| **Last commit** | 2025-11-23 |
| **Links** | [repository](https://github.com/ZaidQureshi/bam) · [benchmark](https://github.com/ZaidQureshi/bam) |

## Verdict

The README quotes the ASPLOS'23 abstract: BFS end-to-end parity (1.0x) and CC 1.49x versus CPU-orchestrated GPU storage access with up to 21.7x lower hardware cost, and 5.3x on proprietary data-analytics queries on the same hardware; compiler flags and CPU model for the paper runs are not on the page. The asplosaoe logs only show functional runs on the artifact machine (e.g. nvm-block-bench on one Intel Optane at 4.90M ops/s, 2.34 GB/s with 512 B requests; one Samsung 980 Pro at 0.80M ops/s, 3.05 GB/s with 4 KiB requests) with no baseline in the same log.

## Use it when

- Graph analytics (BFS, CC, SSSP, PageRank) or similar data-dependent workloads whose working set exceeds GPU memory and lives on NVMe
- You control the whole box: x86 server with PCIe P2P, Volta-or-newer datacenter GPU (V100/A100/H100) and dedicated NVMe SSDs that can be detached from the OS
- Research or prototyping on GPU-initiated I/O where cutting host memory and CPU cost (the paper reports up to 21.7x lower hardware cost) matters as much as speed
- Fine-grained random reads (512 B to 4 KiB) from many GPU threads, where batching through cudaMemcpy or GPUDirect Storage would amplify I/O

## Skip it when

- Anything that needs a filesystem: BaM reads raw NVMe blocks on an SSD unbound from the kernel driver, so datasets must first be written with its readwrite tool
- Consumer GPUs or Tesla T4 (256 MB BAR is too small), Arm servers (open enhancement request), AMD GPUs (no ROCm support), or VMs (open question)
- Production systems: IOMMU and ACS must be disabled, tested on Linux 5.8.x, and the README warns 6.x kernels and post-20.04 Ubuntu P2P changes may break it
- Streaming workloads with known access patterns, where CPU-pipelined transfers are already efficient; the paper's BFS result is parity (1.0x) in time
- When you need the data-analytics path behind the 5.3x claim: that implementation is proprietary and not in the repo

## How it is fast

GPU self-orchestrated storage access: thousands of GPU threads enqueue NVMe commands concurrently into many deep queues (128 queues x 1024 entries in the examples) using ticket-based lock-free submission (atomic fetch_add tickets in nvm_parallel_queue.h). A fine-grained GPU software cache with warp-level request coalescing (__match_any_sync) and round-robin slot allocation cuts I/O amplification, and PCIe peer-to-peer DMA moves data straight from SSD into GPU memory. The gain comes from removing CPU-GPU synchronization and staging for fine-grained, data-dependent access, not from faster per-request I/O.

## Compared with alternatives

Pick BaM over SPDK or liburing only when the consumer of the data is a GPU kernel with data-dependent access: SPDK and io_uring keep the CPU in the I/O path, while BaM lets GPU threads drive the NVMe queues. For loading model weights into GPUs, fastsafetensors or InstantTensor are far easier to deploy.

## Integration

| | |
|---|---|
| **Form** | header-only (CUDA headers in include/) plus static lib (libnvm) and an out-of-tree kernel module |
| **Dependencies** | CUDA 12.3+, NVIDIA driver 440.33+ with compiled kernel symbols, CMake 3.10+ with FindCUDA, git submodules (freestanding, simt atomics), custom libnvm kernel module |
| **Minimum toolchain** | C++11 (CMake sets -std=c++11), GCC 5.4+, CUDA 12.3+; default GPU archs sm_70/80/90 |
| **Platforms** | x86-64 Linux (tested kernel 5.8.x) with PCIe P2P and Above 4G Decoding; NVIDIA Volta or newer datacenter GPU |
| **Thread safety** | Designed for massive concurrency from GPU threads (atomic ticket queues, per-page atomic state); host-side thread safety not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- bam_ptr's operator[] marks cache pages dirty even on reads, so read-only kernels can trigger spurious NVMe writes (issue #56 saw about 35% writes on a Zipfian read benchmark); use seq_read() for reads
- BaM writes to the raw SSD; the README warns not to keep any needed data on it
- Open reports of segfaults and errors in nvm-block-bench (#37 and others), an illegal memory access in vectoradd, and inconsistent load/store after large data volumes
- Graph datasets used in the paper are not public; you must ask the authors

## Known shortcomings

- Issue 56: bam_ptr operator[] marks pages dirty on reads, so read-only runs send spurious NVMe writes (about 35% on the Zipfian bench; workaround seq_read()). The asplosaoe logs are functional runs only, with no baseline (Optane 4.90M ops/s at 512 B; 980 Pro 0.80M ops/s at 4 KiB); the data-analytics 5.3x code is proprietary. Open segfault reports (37) and an illegal memory access in vectoradd. Kernel 5.8.x tested; the README says 6.x may break.

## Caveats and trade-offs

The baseline in the paper is a CPU-orchestrated GPU storage path, not literally POSIX read/write, mmap or io_uring; README quotes the ASPLOS'23 abstract without benchmark setup. The BFS result is 1.0x (parity), with the win being hardware cost. Needs a Volta-or-newer datacenter NVIDIA GPU, a custom kernel module and IOMMU disabled; CUDA 12.3+, GCC 5.4+.

Needs NVIDIA GPU, custom kernel driver, and NVMe SSD detached from the OS; research prototype in CUDA C++.

## Maintenance

Active research artifact (last commit 2025-11-23, 17 open issues), BSD-2-Clause (inherited from Jonas Markussen's ssd-gpu-dma), copyable but tied to a narrow hardware and kernel setup.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Numbers are from the peer-reviewed ASPLOS'23 paper (abstract quoted in the README) comparing GPU self-orchestrated storage access against CPU-orchestrated storage access; the repo is the artifact (asplosaoe/ directory) but compiler flags and CPU model are not stated on the page, so not A.
- **Verifier notes:** Paper itself not opened (ACM blocked); tier B rests on the peer-reviewed venue and README-quoted abstract. Last commit 2025-11-23 (merge of PR #64), so active.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/README.md>
  - <https://github.com/ZaidQureshi/bam>
  - <https://github.com/ZaidQureshi/bam/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/README.md>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/asplosaoe/README.md>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/include/page_cache.h>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/include/nvm_parallel_queue.h>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/asplosaoe/nvm_block_bench_1_sam.log>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/asplosaoe/nvm_block_bench_1_intel.log>
  - <https://raw.githubusercontent.com/ZaidQureshi/bam/HEAD/asplosaoe/nvm_bfs_bench_1_intel.log>
  - <https://github.com/ZaidQureshi/bam/tree/master/include>
  - <https://github.com/ZaidQureshi/bam/issues>
  - <https://github.com/ZaidQureshi/bam/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/ZaidQureshi/bam/issues/56>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/zaidqureshi/bam`) · [data/wave11/enrich/raw/github_com_zaidqureshi_bam.json](../../../data/wave11/enrich/raw/github_com_zaidqureshi_bam.json) (enrichment confidence 0.7)

</details>
