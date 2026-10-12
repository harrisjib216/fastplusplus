# Tiled-MM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Out-of-core GPU GEMM on host-memory matrices for CUDA/ROCm; 2-4.7x faster than default cublasXt, on par with tuned cublasXt at n&gt;=12000.

| | |
|---|---|
| **Beats** | NVIDIA cublasXt (vanilla and manually tuned with 4000 tile size and pinned memory) |
| **Claimed result** | README chart docs/performance.svg (tables of numbers rendered as an image): DGEMM time Tiled-MM vs cublasXt vanilla 83 vs 167 ms at n=4000 up to 16205 vs 76882 ms at n=32000 (2.0x to 4.7x, derived from page data); throughput 4044.18 vs 852.42 GFlop/s at n=32000 (89.87% vs 18.94% of 4500 GFlop/s peak). Against tuned cublasXt: 83 vs 127 ms at n=4000 (1.5x, derived), 352 vs 412 ms at n=8000 (1.17x, derived), and parity within about 1% from n=12000 to 32000 (tuned cublasXt slightly faster at 20000: 4252 vs 4282 ms, and 28000: 11113 vs 11171 ms). |
| **Workload** | Double-precision square column-major GEMM (alpha=beta=1) on matrices stored in host memory, tiled and pipelined to one GPU (also ported to AMD via rocBLAS). |
| **Metric** | throughput |
| **Hardware** | One Piz Daint (Cray XC50) node with an NVIDIA P100 GPU (chart states peak 4500 GFlop/s, CUDA toolkit 10.1); host CPU model not stated |
| **Adoption** | 33 stars; backend of COSMA |
| **Last commit** | 2024-12-06 |
| **Links** | [repository](https://github.com/eth-cscs/Tiled-MM) · [benchmark](https://github.com/eth-cscs/Tiled-MM) |

## Verdict

First-party chart (docs/performance.svg) on one Piz Daint P100 node with CUDA 10.1: double-precision square column-major GEMM with alpha=beta=1 on host matrices. Against default cublasXt it is 83 vs 167 ms at n=4000 (2.0x) up to 4044 vs 852 GFlop/s at n=32000 (4.7x). Against cublasXt tuned to tile 4000 with pinned memory it is 1.5x at n=4000, 1.17x at n=8000, and within about 1% from n=12000 up. Compiler, flags and host CPU are not stated, and the measured 2019 code was later fixed for wrong-result bugs.

## Use it when

- DGEMM/SGEMM/ZGEMM on matrices held in host memory that are too big for the GPU, or that you do not want to manage on the device yourself.
- Replacing a default (untuned) cublasXt setup: the published chart shows 2.0x at n=4000 up to 4.7x at n=32000 on a P100.
- Repeated large multiplies where a reusable context, pre-pinned host buffers and per-dimension tile sizes can be set up once.
- Code that must run on both NVIDIA (CUDA) and AMD (ROCm/rocBLAS) GPUs through one host-pointer GEMM interface.

## Skip it when

- Data already resident on the GPU: call cuBLAS or rocBLAS directly. Tiling and host transfers only add overhead.
- Against a well-tuned cublasXt (tile 4000, pinned memory) at n &gt;= 12000: the chart shows parity, and tuned cublasXt is slightly faster at n=20000 and 28000.
- Half, bf16, int8 or tensor-core mixed precision: only float, double, complex&lt;float&gt; and complex&lt;double&gt; are instantiated, despite the README's 'arbitrary data types'.
- Multi-GPU in one call: multi-device use is not documented (each handle wraps one context; the cublasXt comparison also selected one device). For multi-node GEMM use COSMA.
- Code that cannot tolerate correctness risk without its own tests: wrong-result bugs were fixed in Feb and Jun 2024, and issue #19 (wrong NN results after 2.0 to 2.3) is still open.

## How it is fast

It does tiled, multi-stream pipelining. Tiles of A and B (and of C on the first k-tile when beta != 0) are copied with async 2D memcpys into per-stream device buffers, and each stream runs cuBLAS or rocBLAS GEMM on its tile. Results are copied back on a separate result stream, ordered by events, so PCIe transfers overlap compute. Tile size (default 5000 per dimension) and stream count (default 2) are set per dimension, device buffers persist in the handle across calls, and copy_c_back=false keeps the full C on the device to skip the return copy.

## Compared with alternatives

Pick Tiled-MM for one GPU with host-resident matrices. Pick COSMA (which uses Tiled-MM underneath) or SPLA when the GEMM is distributed across MPI ranks. For device-resident data, the GPU GEMM kernels in this category (cuBLAS or the hand-written kernels) are the comparison, not Tiled-MM.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | CUDA toolkit (cuBLAS, cudart) or ROCm rocBLAS. cxxopts (fetched by CMake) only for tests and examples. |
| **Minimum toolchain** | C++14 (cxx_std_14), CMake 3.17+. README build example uses gcc-8. |
| **Platforms** | Hosts with an NVIDIA GPU (TILEDMM_GPU_BACKEND=CUDA) or an AMD GPU (ROCM). |
| **Thread safety** | not documented. Each mm_handle owns its streams, BLAS handles and device buffers, and gemm() resizes those buffers, so use one handle per thread. |
| **Drop-in for the baseline** | partial — it fills the same role as cublasXt (host pointers, tiling, overlap), but its signature is gpu::gemm with char transpose flags and a Tiled-MM handle, so call sites must be rewritten. |

## Gotchas

- The leading-dimension checks in tiled_mm.cpp build a std::runtime_error but never throw it, so ld_a/ld_b/ld_c smaller than the row count is accepted silently.
- pin_host_buffers defaults to true, so each call registers and unregisters A, B and C with the driver. Allocate with gpu::malloc_pinned and pass false for repeated calls: the benchmark miniapp does this, so published timings exclude pinning.
- The default context preallocates 2 streams x three 5000x5000 tiles, about 1.2 GB of device memory for double (derived from the defaults in mm_handle.hpp). The README's gpu::make_context() example omits the required template argument (make_context&lt;double&gt;()).
- Issue #19 (opened 2024-06-21, no reply) reports wrong results for trans N/N on tall-skinny 46656x152x480 after upgrading from 2.0 to 2.3. A synchronization fix ('incorrect result would sometimes be returned') landed four days later in v2.3.1, but whether it resolves #19 is not documented.

## Known shortcomings

- Two wrong-result bugs fixed in 2024 (Feb: some tile sizes; Jun: a sync issue), after the 2019 measurements; chart sizes do not match examples/compare.sh; vs tuned cublasXt only 1.5x at n=4000, 1.17x at n=8000 and about equal from n=12000 (tuned slightly faster at 20000 and 28000); compiler, flags and host CPU not stated; stale since 2024-12-06.
- tiled_mm.cpp builds std::runtime_error for bad ld_a/ld_b/ld_c but never throws, so bad leading dimensions pass silently; open #19 (since 2024-06-21): wrong NN results at 46656x152x480 after 2.0 to 2.3, no reply; only float/double/complex instantiated despite 'arbitrary data types'.

## Caveats and trade-offs

Numbers exist only inside the README's chart image (docs/performance.svg), not in text. The clear win is over vanilla cublasXt (2.0-4.7x); against a hand-tuned cublasXt (tile 4000, pinned memory) it is 1.5x at n=4000 and 1.17x at n=8000 and only on par from n=12000 upward. Compiler and flags for the run are not stated (README build example uses gcc-8; CMake defaults to Release); host CPU not stated. The chart sizes (4000-32000) do not match examples/compare.sh (4000-20000), so the exact run script is not published. Correctness bugs were fixed after the 2019 measurements ('Fixed the wrong results bug for certain tile sizes', Feb 2024; synchronization issue that 'would sometimes' return an incorrect result, Jun 2024). P100/CUDA 10.1-era data. Baseline cublasXt is not one of OpenBLAS, MKL, Eigen or BLIS.

Host-pointer tiled GEMM for CUDA or ROCm; user-selectable tile size per dimension and stream count; reusable context for repeated calls; templated over data types.

## Maintenance

Stale but not abandoned: last commit 2024-12-06 (CMake/FetchContent cleanup; issue #24 notes a v2.3.2 git tag), maintained mainly as COSMA's backend. BSD-3-Clause and small (about 20 source files), so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README benchmark against vanilla and tuned cublasXt with public benchmark code (examples/multiply.cpp, examples/cublasXt-multiply.cpp, examples/compare.sh) and GPU model plus CUDA 10.1 stated, but the compiler, flags and host CPU model of the run are not stated and the measured 2019 code was later fixed for wrong-result bugs, so it stays C. Not peer-reviewed.
- **Verifier notes:** README text has no numbers, but the embedded performance.svg is a table of timings/throughputs plus a bar chart (rendered locally); the record understated the evidence. License BSD-3-Clause, 33 stars, not archived, not a fork, last commit 2024-12-06 (stale) all confirmed. Wrong-result bug fixes in 2024 are worth recording as a shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eth-cscs/Tiled-MM>
  - <https://github.com/eth-cscs/Tiled-MM/commits>
  - <https://github.com/eth-cscs/Tiled-MM/tree/master/examples>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/docs/performance.svg>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/compare.sh>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/cublasXt-multiply.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/eth-cscs/Tiled-MM/tree/master/src/Tiled-MM>
  - <https://github.com/eth-cscs/Tiled-MM/issues?q=is%3Aissue>
  - <https://github.com/eth-cscs/Tiled-MM/issues/19>
  - <https://github.com/eth-cscs/Tiled-MM/commits/master>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/compare.sh>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/multiply.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/cublasXt-multiply.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/examples/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/tiled_mm.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/tiled_mm.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/mm_handle.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/mm_handle.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/gpu_context.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/Tiled-MM/HEAD/src/Tiled-MM/util.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eth-cscs/tiled-mm`) · [data/wave8/enrich/raw/github_com_eth_cscs_tiled_mm.json](../../../data/wave8/enrich/raw/github_com_eth_cscs_tiled_mm.json) (enrichment confidence 0.75)

</details>
