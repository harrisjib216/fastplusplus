# GPU Programming with C++ and CUDA: two-stream chunked copy and compute overlap for vector-matrix multiply (chapter 8)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `MIT` · 🟡 stale

> Book CUDA pattern: row chunks copied from pinned memory on two streams so transfers overlap the GEMV kernel.

| | |
|---|---|
| **Beats** | same CUDA vector-matrix multiply without streams (one blocking copy of the whole matrix, then one kernel, then one copy back) |
| **Claimed result** | Book Table 8.1 (relayed via the seed lead from the book, not shown on any repo page I opened): 25 to 31% lower execution time with streams; best 27.05% (87.03 ms) at 1020 MB and 31.37% (343.555 ms) at 4092 MB, averages of ten runs, chunks near 100-200 MB. The repo's commented-out average() calls hold the no-streams reference times 119.299 ms (16,380 matrix) and 500.615 ms (32,760 matrix); 87.03 against 119.299 and 343.555 against 500.615 reproduce the 27.05% and 31.37% (derived from page data plus the relayed averages). |
| **Workload** | Float matrix times vector for 16,380 x 16,380 and 32,760 x 32,760 matrices: matrix split into row chunks (273 to 16,380 rows) copied with cudaMemcpyAsync on two alternating streams so copy and kernel overlap, against vec_mat_mul_nostreams.cu; end-to-end GPU time with CUDA events, copies included. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-10750H and NVIDIA GeForce RTX 2060, per the book (relayed via lead; no hardware is listed on a repo page); PCIe transfer rate measured near 12 GB/s per the book |
| **Compiler and flags** | Not stated. ch8/3_multiplying_with_streams/CMakeLists.txt (project language CUDA, cmake_minimum_required 3.10) adds the two executables with no flags, no build type and no CMAKE_CUDA_ARCHITECTURES, so nvcc's defaults apply. Repo README lists g++ 9.4, CUDA Toolkit 12 and CMake 3.16 as the environment but no flags. |
| **Adoption** | 117 stars; Packt companion repository of the book GPU Programming with C++ and CUDA (2025) |
| **Last commit** | 2025-12-15 |
| **Links** | [repository](https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA) · [benchmark](https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/blob/main/ch8/3_multiplying_with_streams/vec_mat_mul_streams.cu) |

## Verdict

The book's Table 8.1, relayed by the seed lead and not in the repo, reports ten-run averages on an Intel Core i7-10750H with a GeForce RTX 2060: the streamed version took 87.03 ms for the 16,380 x 16,380 float matrix (printed as 1020 MB) and 343.555 ms for 32,760 x 32,760 (4092 MB), 27.05% and 31.37% below the no-streams reference times of 119.299 ms and 500.615 ms that appear in the repo's commented-out calls, with 25-31% across chunk sizes. End-to-end GPU time including all copies is measured with CUDA events; compiler flags are not stated and CMakeLists.txt sets none, which matters little for a transfer-bound timing.

## Use it when

- A kernel whose input must cross PCIe on every call and whose compute time is comparable to the transfer time, so overlap can hide the smaller of the two.
- Matrices or datasets larger than GPU memory: the streamed version needs only two chunk buffers on the device, while the no-streams baseline allocates the whole matrix (4.29 GB at 32,760 rows) on the GPU.
- Data that already lives in, or can be produced directly into, pinned host memory, such as a reusable staging buffer.
- Tuning chunk size for a given PCIe link and GPU: the repo sweeps 273 to 16,380 rows per chunk, and the book (relayed) found chunks near 100-200 MB best.

## Skip it when

- Data that stays on the GPU or is reused by many kernels: copy it once and keep it resident; overlap only pays when every call streams fresh data across PCIe.
- One-off matrix-vector products on host data: the work is capped by the roughly 12 GB/s transfer the book reports, so a multithreaded CPU GEMV reading host memory directly may beat both GPU versions; the repo's CPU loop is naive scalar code and its times are not published.
- When pinning must be paid for: the full matrix (1 to 4 GB) is allocated with cudaMallocHost and filled outside the timed region, so an application that receives data in pageable memory still pays to pin or copy it, and the 27-31% does not include that.
- As a fast GEMV kernel: one thread per row reads row-major data with a whole row between adjacent threads (uncoalesced), small chunks launch tiny grids (2 blocks of 256 threads at 273 rows), and cuBLAS is not compared.
- Row counts that are not a multiple of twice the chunk size: the loop has no tail handling and would read and write past the end of its buffers.

## How it is fast

Copy/compute overlap with double buffering (software pipelining over CUDA streams): while one stream's kernel works on chunk k, the copy engine is already moving the next chunk for the other stream, so kernel time and the small result copies hide behind the host-to-device transfer. Pinned (page-locked) host memory lets cudaMemcpyAsync run asynchronously and also transfers faster than pageable memory. Every matrix element is used once, so the job is bound by PCIe bandwidth: the book's best streamed times work out to about 12.3 and 12.5 GB/s against about 9.0 and 8.6 GB/s for the no-streams reference times (derived from page data plus the relayed averages), close to the roughly 12 GB/s pinned rate the book reports.

## Compared with alternatives

Pick this over the other GPU Programming with C++ and CUDA entries when host-device transfer, not kernel speed, dominates: the ch4 vector-add entry times blocking copies and the kernel one after another, the prime entry moves no data at all, and the ch7 tiled matrix multiply speeds up the kernel itself, which this transfer-bound job would barely notice.

## Integration

| | |
|---|---|
| **Form** | source-drop (pattern shown in two .cu programs) |
| **Dependencies** | CUDA runtime only (cuda_runtime.h); the repo's devcontainer installs CUDA Toolkit 12.0 and g++ 9 on Ubuntu 20.04 |
| **Minimum toolchain** | CUDA toolkit with streams and cudaMallocHost (the repo targets CUDA 12); CMake 3.10+ per CMakeLists.txt; README lists CUDA Toolkit 12, g++ 9.4 and CMake 3.16 |
| **Platforms** | NVIDIA GPUs with at least one asynchronous copy engine; ch8/2_mem_bandwidth/mem_bandwidth.cu prints the async engine count and concurrent-kernel support, and memcpy_benchmark.cu measures pinned host-to-device bandwidth from 1 MB to 1 GB |
| **Thread safety** | not documented; each compute() call creates and destroys its own streams and buffers and shares nothing between host threads |
| **Drop-in for the baseline** | partial — same kernel and results, but the matrix must sit in pinned memory, two device chunk buffers replace the full device matrix, and the row count must be a multiple of twice the chunk size |

## Gotchas

- The comparison changes two things at once: the baseline copies from pageable malloc memory and the streamed version from pinned cudaMallocHost memory, and the repo has no pinned no-streams variant, so how much of the 27-31% is overlap rather than faster pinned transfers is unmeasured; ch8/2_mem_bandwidth/memcpy_benchmark.cu measures pinned bandwidth only, never pageable.
- The no-streams reference times (119.299 ms and 500.615 ms) are constants in commented-out average() calls; the no-streams program times one pass per size and the code tells you to replace the constants with your own measurement, so the printed percentage gain compares a ten-run average with a single number from another program and run.
- No CUDA call is error-checked: a failed 4.29 GB cudaMallocHost (not enough RAM or a locked-memory limit) leaves a null pointer that initializeMatrix then writes through. The timed region also includes a blocking copy of the input vector from pageable memory and the creation of both streams.
- checkResult uses an absolute tolerance of 1e-3, only a few float ulps for row sums in the thousands (matrix and vector values are uniform in [0, 1]), so any rounding difference between the GPU and CPU loops, such as a fused multiply-add on one side, can print a spurious mismatch; it reports only the first one.

## Known shortcomings

- Book times are not in the repo (only reference times in commented-out code reproduce the 27.05% and 31.37%). Pinned against pageable memory is confounded with overlap; the streamed run moves about 12.3-12.5 GB/s (derived from page data), so it is transfer-bound and the overlap share is unmeasured. Stream creation sits inside the timed region; naive uncoalesced kernel, tiny grids; no flags or CUDA arch. Loose category fit.
- Enricher: host-memory pinning outside the timed region favours streams; one pass against a 10-run average; pinned-memory and overlap gains never separated; no error checks; repo stale since 2025-08-20.

## Caveats and trade-offs

The two programs differ in more than streams: the baseline allocates the matrix with malloc (pageable memory) while the streams version uses cudaMallocHost (pinned memory), so part of the gain is faster pinned-memory transfers rather than overlap; the repo does not isolate the two effects (no pinned, no-stream variant). The relayed best times correspond to about 12.3 GB/s (1.07 GB matrix in 87.03 ms) and 12.5 GB/s (4.29 GB matrix in 343.555 ms) against about 9.0 and 8.6 GB/s for the no-streams reference times (derived from page data plus the relayed averages), close to the pinned PCIe rate the book reports, so the streamed version is transfer-bound and the share of the 27-31% that comes from hiding the kernel rather than from pinned memory is unmeasured. The no-streams reference times in the comments are single values from the author's machine (the code says to replace them with your own measurement) and the book's ten-run averages are not stored in the repo; the comparison is across two separate programs and runs. The streams version creates its two streams inside the timed region (a small cost against it). The kernel uses one thread per row with strided, uncoalesced row-major reads, and small chunks launch tiny grids (2 blocks of 256 threads at 273 rows), so neither side is a tuned GEMV and cuBLAS is not compared. The chunk loop assumes the row count is a multiple of twice the chunk size, which holds for every size in main(). The CPU run in compute() is skipped in the averaging path. Timing includes the result copy back and the stream synchronisation. Tier C: first-party, hardware from the book only. Files opened: ch8/3_multiplying_with_streams/vec_mat_mul_streams.cu, vec_mat_mul_nostreams.cu, CMakeLists.txt, ch8/readme.md, README.md. [retier] Enricher: cudaMallocHost pinning of 1-4 GB happens outside the timed region, which favours the streams version; the no-streams program times one pass while the streams figure is a 10-run average; memcpy_benchmark.cu measures pinned bandwidth only, so the repo never separates the pinned-memory gain from the overlap gain. No CUDA error checks; checkResult's 1e-3 tolerance can print false mismatches; no tail handling for sizes that are not a multiple of the chunk. Upside: chunking lets the matrix exceed GPU memory. CMakeLists set no flags, build type or CUDA architectures.

Needs pinned host memory, a chunk size tuned to the PCIe bandwidth and kernel speed, and extra device buffers; the matrix-vector kernel is bandwidth-bound so most of the saving is hidden transfer time. NVIDIA GPU and CUDA toolkit required.

## Maintenance

MIT-licensed Packt companion repo (117 stars, 40 forks) that is effectively frozen since publication: last code change 2025-08-20, last commit a README banner on 2025-12-15, and PR #1 (open since 2025-10-07, touches these files only to drop a zero initialisation) and issue #3 (another chapter, open since 2026-02-04) have no maintainer reply, so 'stale' fits better than 'active'; copy the pattern, adding error checks, tail handling and a pinned no-streams control.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** ch8/3_multiplying_with_streams/vec_mat_mul_streams.cu and vec_mat_mul_nostreams.cu implement the streamed and unstreamed versions with CUDA-event timing, but the repo holds code only: the 87.03 ms and 343.555 ms averages are the book's own run relayed by the lead, only the no-streams reference times 119.299 and 500.615 ms appear (in commented-out average() calls), and no flags or CPU/GPU are stated in the repo. First-party, partial methodology, so C.
- **Verifier notes:** Source matches the record: two alternating streams with cudaMemcpyAsync from pinned memory against one blocking pageable copy, and 27.05% and 31.37% reproduce from the relayed averages and the commented reference times (the program's own gain formula is 100 - average/reference\*100; 1020 MB and 4092 MB are its integer-rounded total sizes). Added the transfer-bound derivation, stream creation inside the timed region and the kernel launch-shape caveats. Metadata confirmed: MIT, 117 stars, 40 forks, not a fork or archived, last commit 2025-12-15 (a README banner update; last code change 2025-08-20), active; category math-simd-linear-algebra is a loose fit for a CUDA copy/compute overlap technique.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-81 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/blob/main/ch8/3_multiplying_with_streams/vec_mat_mul_streams.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/3_multiplying_with_streams/vec_mat_mul_streams.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/3_multiplying_with_streams/vec_mat_mul_nostreams.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/3_multiplying_with_streams/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/readme.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/LICENSE>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/commits/main>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/tree/main/ch8>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/3_multiplying_with_streams/vec_mat_mul_streams.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/3_multiplying_with_streams/vec_mat_mul_nostreams.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/3_multiplying_with_streams/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/readme.md>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/tree/main/ch8/2_mem_bandwidth>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/2_mem_bandwidth/mem_bandwidth.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/2_mem_bandwidth/memcpy_benchmark.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/2_mem_bandwidth/CMakeLists.txt>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/tree/main/ch8/1_vector_add>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch8/1_vector_add/vector_add.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/ch4/2_vector_add/vector_add.cu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/.devcontainer/DockerfileUbuntu>
  - <https://raw.githubusercontent.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/HEAD/.devcontainer/devcontainer.json>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/commits/main>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/issues/3>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/pulls>
  - <https://github.com/PacktPublishing/GPU-Programming-with-CPP-and-CUDA/pull/1/files>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-gpu-programming-with-cpp-and-cuda-stream-overlap`) · [data/wave1/enrich/raw/paper_book_gpu_programming_with_cpp_and_cuda_stream_overlap.json](../../../data/wave1/enrich/raw/paper_book_gpu_programming_with_cpp_and_cuda_stream_overlap.json) (enrichment confidence 0.6)

</details>
