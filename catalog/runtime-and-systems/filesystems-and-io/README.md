# Filesystems and I/O

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md)</sub>

**What these beat:** POSIX read/write, mmap, io_uring baselines  
**50 entries:** 1 tier A · 11 tier B · 34 tier C · 4 tier D · 42 copyable, 8 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**zlob**](dmtrkovalenko-zlob.md) | Zig glob(3)-compatible globbing and parallel file walker with C/Rust APIs; about 2-3x faster than Rust glob crate and walkdir. | **A** | Zig | MIT | 🟢 active |
| 2 | [**liburing**](axboe-liburing.md) | Userspace wrapper around Linux's io_uring ring-buffer syscall interface; beats libaio and POSIX-AIO on IOPS and syscall overhead. | **B** | C | MIT OR LGPL-2.1-or-later | 🟢 active |
| 3 | [**htslib**](samtools-htslib.md) | C library for SAM/BAM/CRAM/VCF/BCF I/O; 5x faster BAM read-write and 13x faster BAM-to-SAM than Samtools 0.1.19 at 16 threads. | **B** | C | MIT AND BSD-3-Clause | 🟢 active |
| 4 | [**Direct register access (BSRR) in bare-metal C, Packt…**](paper-book-bare-metal-embedded-c-programming-direct-register-access-gpio.md) | Drive STM32 GPIO pins with single stores to the BSRR register instead of calling HAL_GPIO_WritePin. | **B** | C | MIT | 🟢 active |
| 5 | [**BaM (Big accelerator Memory)**](zaidqureshi-bam.md) | CUDA library and kernel driver that let GPU threads issue NVMe reads and writes themselves, bypassing CPU-orchestrated storage paths. | **B** | C++ | BSD-2-Clause | 🟢 active |
| 6 | [**FastMap**](carv-ics-forth-fastmap.md) | Linux 4.14 kernel module replacing the mmap page-fault and eviction path for fast block devices; 3.7-7x more page faults/s than mmap at high thread counts. | **B** | C | LGPL-2.1 | 🟡 stale |
| 7 | [**XRP (BPF-KV, WiredTiger patches)**](xrp-project-xrp.md) | OSDI'22 research kernel that lets an eBPF function in the NVMe driver chain dependent reads, beating read() and io_uring for on-disk B-tree lookups. | **B** | C | Apache-2.0 | 🔴 abandoned |
| 8 | [**SplitFS**](utsaslab-splitfs.md) | LD_PRELOAD user-space persistent-memory file system layered on ext4 DAX; cuts POSIX data-path overhead versus ext4 DAX and NOVA. | **B** | C | Apache-2.0 | 🔴 abandoned |
| 9 | [**Trio / ArckFS**](rs3lab-trio.md) | SOSP '23 research userspace NVM file system (ArckFS) on Optane PM that outscales NOVA, WineFS, OdinFS and ext4-DAX at high core counts. | **B** | C | Apache-2.0 | 🔴 abandoned |
| 10 | [**vldb26-iouring (io_uring for DBMSs artifact)**](mjasny-vldb26-iouring.md) | VLDB'26 artifact measuring which io_uring settings speed up DBMS buffer managers and network shuffles compared with default io_uring and epoll. | **B** | C++ | no license (study only) | 🟢 active |
| 11 | [**MadFS**](shawnzhong-madfs.md) | LD_PRELOAD userspace persistent-memory file layer over ext4-DAX; FAST '23 reports up to 3.6x ext4-DAX concurrent throughput. | **B** | C++ | no license (study only) | 🔴 abandoned |
| 12 | [**WineFS**](utsaslab-winefs.md) | Linux kernel file system for Intel Optane persistent memory that keeps 2MB hugepage mappings after aging; beats ext4-DAX, xfs-DAX, NOVA on mmap workloads. | **B** | C | CC-BY-NC-4.0 (study only) | 🔴 abandoned |
| 13 | [**ripgrep**](burntsushi-ripgrep.md) | Recursive regex search CLI in Rust; beats GNU grep, git grep, ag and ugrep on code trees and large files. | **C** | Rust | MIT OR Unlicense | 🟢 active |
| 14 | [**gdu**](dundee-gdu.md) | Parallel Go disk usage analyzer (TUI, CLI and web UI); scans about 6.5x faster than GNU du on a cold SSD. | **C** | Go | MIT | 🟢 active |
| 15 | [**SPDK**](spdk-spdk.md) | Userspace, polled-mode NVMe driver and storage stack that beats kernel io_uring/libaio on IOPS per core. | **C** | C | BSD-3-Clause | 🟢 active |
| 16 | [**libarchive (bsdtar)**](libarchive-libarchive.md) | Multi-format streaming archive library behind bsdtar; matches or trails GNU tar on tar speed, wins only seek-based listing. | **C** | C | BSD-2-Clause | 🟢 active |
| 17 | [**bfs**](tavianator-bfs.md) | Breadth-first, find-compatible directory search tool with parallel async I/O; about 3x faster than GNU find on full traversals. | **C** | C | 0BSD | 🟢 active |
| 18 | [**diskus**](sharkdp-diskus.md) | Parallel Rust replacement for du -sh that prints one directory total; author measured 10x faster cold-cache, 2.2x warm. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 19 | [**fcp**](svetlitski-fcp.md) | Parallel Rust replacement for the common cp -R cases; about 10x faster than GNU cp on a Linux kernel tree on SSD. | **C** | Rust | BSD-3-Clause | 🟢 active |
| 20 | [**parallel-disk-usage (pdu)**](ksxgithub-parallel-disk-usage.md) | Rust disk-usage analyzer (pdu) that walks directories in parallel with rayon; about 2.2x faster than GNU du warm-cache. | **C** | Rust | Apache-2.0 | 🟢 active |
| 21 | [**Run:ai Model Streamer**](run-ai-runai-model-streamer.md) | Concurrent C++ safetensors reader with a Python API that loads model weights to GPU faster than Hugging Face's safetensors loader. | **C** | C++ | Apache-2.0 | 🟢 active |
| 22 | [**xNVMe**](xnvme-xnvme.md) | Samsung's single C API for NVMe I/O over io_uring, io_uring_cmd, libaio, SPDK and more; DuckDB on it beats default sync I/O. | **C** | C | BSD-3-Clause | 🟢 active |
| 23 | [**fastsafetensors**](foundation-model-stack-fastsafetensors.md) | Python safetensors loader with a C++17 pybind11 core that replaces mmap with parallel pread/GDS reads into GPU memory. | **C** | Python | Apache-2.0 | 🟢 active |
| 24 | [**UMap**](llnl-umap.md) | LLNL user-space mmap replacement built on userfaultfd; beats Linux mmap for large-page, out-of-core reads with tuned paging. | **C** | C++ | LGPL-2.1 | 🟢 active |
| 25 | [**DAXFS**](multikernel-daxfs.md) | Linux kernel filesystem on DAX memory with lock-free CAS overlay; authors report up to 2.68x tmpfs random-write throughput. | **C** | C | GPL-2.0 | 🟢 active |
| 26 | [**vmcache (with exmap)**](viktorleis-vmcache.md) | Single-file C++20 database buffer manager that uses virtual memory for page translation; beats mmap-based LMDB and WiredTiger on TPC-C. | **C** | C++ | MIT | 🟢 active |
| 27 | [**InstantTensor**](scitix-instanttensor.md) | C++/Python safetensors-to-GPU loader using O_DIRECT io_uring/AIO plus NCCL all-gather; beats the safetensors loader on cold loads. | **C** | C++ | Apache-2.0 | 🟢 active |
| 28 | [**TriCache**](thu-pacman-tricache.md) | User-space multi-level block cache over SPDK SSDs that runs unmodified in-memory programs out-of-core, beating Linux swap and mmap. | **C** | C++ | Apache-2.0 | 🟢 active |
| 29 | [**RFUSE**](snu-csl-rfuse.md) | FAST '24 research FUSE replacement: per-core shared-memory ring channels and hybrid polling; about 2.27x FUSE random-read throughput (paper snippet). | **C** | C | GPL-2.0 | 🟢 active |
| 30 | [**lsr**](rockorager-lsr.md) | Zig ls(1) clone that batches directory open, statx and passwd/group/localtime reads through io_uring; beats GNU ls -al. | **C** | Zig | MIT | 🟢 active |
| 31 | [**ayafileio**](patchouli-cn-ayafileio.md) | Python async file I/O with a C++ native core on io_uring, IOCP and Dispatch I/O; beats thread-pool aiofiles on small cached reads. | **C** | Python | MIT | 🟢 active |
| 32 | [**FluxIO**](programminggod-byte-fluxio.md) | Header-only C++20 io_uring (SQPOLL, fixed files and buffers) O_DIRECT block I/O engine; out-runs Boost.Asio file I/O and Go on 4 KiB writes. | **C** | C++ | MIT | 🟢 active |
| 33 | [**uring-sync**](vincentdu2021-uring-sync.md) | Linux io_uring directory copier and kTLS network sender for many-small-file trees; beats cp -r locally and rsync -az over SSH. | **C** | C++ | MIT | 🟢 active |
| 34 | [**wudream813/fastio**](wudream813-fastio.md) | Single-header C++17 fast integer reader/writer for competitive programming: mmap plus 2-digit lookup tables, about 7-8x faster than std::cin. | **C** | C++ | MIT | 🟢 active |
| 35 | [**zdu**](lxl66566-zdu.md) | Parallel Rust disk-usage CLI with a dust-style tree chart; 2.7-10x faster than dust, mixed against pdu. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 36 | [**fclones**](pkolaczk-fclones.md) | Parallel, device-aware Rust duplicate file finder; 4-10x shorter wall time than jdupes, fdupes and rdfind on a 316 GB SSD scan. | **C** | Rust | MIT | 🟡 stale |
| 37 | [**al-dente (dent)**](royreznik-al-dente.md) | Small multithreaded C directory walker on raw getdents64 that prints every path; beats GNU find and fd on a synthetic tree. | **C** | C | MIT | 🟡 stale |
| 38 | [**rawscan**](thepythoniccow-rawscan.md) | Small Linux C line reader over a raw fd; about 30-40% less user CPU than fgets or getline on large inputs. | **C** | C | Apache-2.0 OR MIT OR… | 🟡 stale |
| 39 | [**NOVA (linux-nova)**](nvsl-linux-nova.md) | Research Linux kernel file system for persistent memory; per-inode logs beat ext4-DAX, xfs-DAX, PMFS and btrfs on write-heavy workloads. | **C** | C | GPL-2.0 | 🔴 abandoned |
| 40 | [**wcp**](wheybags-wcp.md) | Experimental io_uring recursive file copier for Linux, about 2-3x faster than GNU cp -r on the author's NVMe box. | **C** | C++ | MIT | 🔴 abandoned |
| 41 | [**rust-linereader**](freaky-rust-linereader.md) | Small Rust buffered reader returning borrowed line slices; beats std BufRead::read_until and lines() for byte-oriented line scanning. | **C** | Rust | MIT | 🔴 abandoned |
| 42 | [**ptar**](zgiles-ptar.md) | Go CLI that archives a directory tree into N independent tar files in parallel, much faster than GNU tar on parallel filesystems. | **C** | Go | MIT | 🔴 abandoned |
| 43 | [**file_io_benchmark (Windows unbuffered multi-threaded…**](m-schuetz-file-io-benchmark.md) | Windows benchmark showing multi-threaded FILE_FLAG_NO_BUFFERING reads reach 11.3 GB/s on NVMe versus fread and memory mapping. | **C** | C++ | no license (study only) | 🟢 active |
| 44 | [**copy-fast**](rushmanthnalluri-copy-fast.md) | Student C11 Linux file-copy tool with threaded pipeline and io_uring backends, compared only against its own naive read/write loop. | **C** | C | no license (study only) | 🟢 active |
| 45 | [**couring**](pabloariasal-couring.md) | Single-file C++20 teaching demo comparing blocking reads, a thread pool, raw io_uring and io_uring coroutines for loading OBJ files. | **C** | C++ | MIT (study only) | 🔴 abandoned |
| 46 | [**liburing_b3sum**](1f604-liburing-b3sum.md) | Demo BLAKE3 file hasher in C/C++ that reads through io_uring and beats Rust b3sum on cold-cache NVMe reads. | **C** | C | no license (study only) | 🔴 abandoned |
| 47 | [**libuv io_uring file backend**](libuv-libuv.md) | libuv's optional Linux io_uring path for uv_fs_\* calls, replacing threadpool hand-off; off by default since 1.49. | **D** | C | MIT | 🟢 active |
| 48 | [**LLFIO**](ned14-llfio.md) | Low-level, zero-copy, race-free C++17 file and memory-map i/o library; no head-to-head numbers against POSIX read/write. | **D** | C++ | Apache-2.0 OR BSL-1.0 | 🟢 active |
| 49 | [**STM32 Low Layer (LL) driver library**](stmicroelectronics-stm32f4xx-hal-driver.md) | ST's Low Layer (LL) drivers: static inline register-access calls that replace HAL calls such as HAL_GPIO_WritePin. | **D** | C | BSD-3-Clause | 🟢 active |
| 50 | [**hop**](jarred-sumner-hop.md) | Uncompressed, read-only archive format and CLI in Zig with an indexed footer, for pulling single files faster than tar or unzip. | **D** | Zig | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
