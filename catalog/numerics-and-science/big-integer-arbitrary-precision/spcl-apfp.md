# APFP (arbitrary precision floating point on FPGA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🔴 abandoned

> Vitis HLS FPGA design for fixed-width arbitrary-precision floating-point matrix multiply, about 10x a 36-core MPFR node (FCCM'22).

| | |
|---|---|
| **Beats** | GNU MPFR (dual-socket 36-core Xeon node) |
| **Claimed result** | README: 2.0 GMAC/s of 512-bit matrix-matrix multiplication on an Alveo U250, 'an order of magnitude higher than a 36-core dual-socket Xeon node, corresponding to 375x CPU cores worth of throughput'. The FCCM'22 abstract, seen only in WebSearch summaries (arXiv 2204.06256, spcl.inf.ethz.ch and ar5iv were blocked), reports versus MPFR on that node: 9.8x at 4.8 GOp/s for 512-bit multiplication, 5.3x at 1.2 GOp/s for 1024-bit multiplication (more than 351x and 191x CPU cores), and 10x at 2.0 GOp/s for matrix multiplication. |
| **Workload** | Fully pipelined Karatsuba-based arbitrary precision floating-point multiplier and adder, exposed as a tiled matrix-multiplication primitive, on an Alveo U250 FPGA versus a dual-socket 36-core Xeon node running MPFR; 512-bit and 1024-bit multiplication and 512-bit matrix-matrix multiplication. |
| **Metric** | throughput |
| **Hardware** | Xilinx Alveo U250 FPGA (Vitis HLS, XRT) versus a dual-socket 36-core Xeon node (CPU model not stated in the README) |
| **Adoption** | 41 stars, 7 forks, 153 commits; peer-reviewed at FCCM 2022 (ETH Zurich SPCL) |
| **Last commit** | 2022-05-17 |
| **Links** | [repository](https://github.com/spcl/apfp) · [benchmark](https://github.com/spcl/apfp) |

## Verdict

The README repeats the FCCM'22 result: 2.0 GMAC/s of 512-bit matrix-matrix multiplication on an Alveo U250, about ten times a dual-socket 36-core Xeon node running MPFR (375 CPU cores' worth); search summaries of the paper abstract add 9.8x at 4.8 GOp/s for 512-bit and 5.3x at 1.2 GOp/s for 1024-bit multiplication. The repo's host programs (host/Microbenchmark.cpp, host/TestMatrixMultiplication.cpp) do time and print an MPFR reference, but it is a single-threaded triple loop of mpfr_mul and mpfr_add used for bit-exact verification, not the 36-core baseline; the CPU model, compiler, flags and MPFR version of the paper's baseline are not in the repo.

## Use it when

- Large dense matrix multiplications at 448-bit or 960-bit mantissa precision (APFP_BITS 512 or 1024) that dominate a run, such as the semidefinite-programming solvers the paper targets.
- You already have an Alveo U250 (or another XRT platform you are willing to port the DDR mapping to) and a Vitis HLS toolchain.
- Throughput matters more than latency: matrices large enough to fill 32x32 tiles and amortize host-to-card transfers.
- Research on FPGA arithmetic: the Karatsuba and pipelined-adder templates are a compact reference for wide-integer datapaths in HLS.

## Skip it when

- Anything other than matrix multiply: no division, square root, transcendental functions or element-wise kernels, and the host interface's transpose is unimplemented; use MPFR, or a GPU MPFR backend for batched scalars.
- When you need MPFR's rounding modes or special values: only round-toward-zero (MPFR_RNDZ) is supported, the adder flushes underflow to zero, and PackedFloat asks 'Should we just assume nan/inf can't appear?'.
- Precision chosen at run time or not a multiple of 512 bits: APFP_BITS is fixed at build time and CMake rejects values not aligned to 512.
- Products you need to ship or redistribute: the repository has no license file, and it has been inactive since 2022-05-17.
- Machines without an FPGA, or teams without days for hardware builds: 'make hw' runs a full Vitis synthesis and place-and-route.

## How it is fast

The mantissa multiplier is a compile-time recursive Karatsuba decomposition (device/Karatsuba.cpp) that bottoms out at APFP_MULT_BASE_BITS (default 36) in DSP multipliers, and wide additions are split into manually pipelined stages above APFP_ADD_BASE_BITS, so the whole multiply-accumulate is fully pipelined at one MAC per cycle per compute unit. The GEMM is tiled with the communication-avoiding scheme from the authors' FPGA'20 paper (default 32x32 tiles in on-chip memory) so DRAM bandwidth does not limit it, and APFP_COMPUTE_UNITS replicates the kernel across the U250's DDR banks and SLRs.

## Compared with alternatives

Pick APFP over MPLAPACK's quad-double or CUDA backends, MultiFloats.jl or DoubleFloats.jl when you need far more than \~200 bits of mantissa in GEMM and own an Alveo U250; pick gnu-mpfr-cgbn or MPLAPACK instead if you have a GPU or need operations other than matrix multiply.

## Integration

| | |
|---|---|
| **Form** | FPGA bitstream (.xclbin) built with Vitis, driven from your own host code; the ApfpHostlib shared library is unfinished (see gotchas) |
| **Dependencies** | Xilinx Vitis HLS and XRT, GMP, MPFR, Threads, hlslib (git submodule) |
| **Minimum toolchain** | C++17 (-std=c++17 in CMakeLists.txt), CMake 3.0+, Vitis version not stated |
| **Platforms** | Xilinx XRT FPGAs; default platform xilinx_u250_gen3x16_xdma_3_1_202020_1, DDR bank mapping hard-coded for the U250; CPU-only simulation build for testing |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The installable host library (interface/Apfp.cpp) looks unfinished: DeviceMatrix::TransferToHost copies the raw device format (kBytes per number, 128 bytes at the default 1024 bits) straight into the caller's mpf_t array, which overruns a buffer of 24-byte mpf_t structs and produces no valid GMP values, and its size check (&gt;=) rejects an exactly sized buffer. The kernel path is an empty string, ApfpHostlib is compiled with HLSLIB_SIMULATE_OPENCL, and Transpose/TransposeInPlace just throw. The benchmark programs in host/ do not use this interface.
- APFP_BITS counts the whole number: 64 bits go to the packed sign and exponent, so 512-bit numbers have a 448-bit mantissa and 1024-bit numbers a 960-bit mantissa.
- Only MPFR_RNDZ is supported (DeviceTypes.h: 'the only MPFR rounding mode supported'); the test programs check bit-exact equality against an MPFR RNDZ reference, so results match MPFR only under round-toward-zero.
- Tile sizes, compute units, frequency and the DDR bank mapping (hard-coded for the U250) must be configured for the target card; the README says the accelerator 'should always be configured to match the target system'.

## Known shortcomings

- No license; CPU-side MPFR harness not public; MPFR ratios (9.8x, 5.3x, 10x) seen only in an abstract summary (paper blocked); FPGA hardware.
- Security/correctness bug in interface/Apfp.cpp: TransferToHost copies 128 bytes per number raw into an mpf_t array (24 bytes each), overflowing the buffer and producing no valid values; size check off by one (&gt;=); the host library builds with HLSLIB_SIMULATE_OPENCL and Transpose throws; benchmarks do not use this interface; only MPFR_RNDZ, flush-to-zero, no NaN/Inf; the MPFR reference is single-threaded.

## Caveats and trade-offs

No LICENSE file (LICENSE, LICENSE.md, LICENSE.txt and COPYING all 404; none shown on the GitHub page), so the code is reference only. Hardware design for Xilinx XRT FPGAs (Vitis HLS), not a CPU library. The README does not name MPFR; the repo builds with MPFR semantics by default (APFP_SEMANTICS=MPFR) and uses mpfr_mul only as an untimed correctness reference (host/MatrixMultiplicationReference.cpp), so the CPU-baseline harness is not public. The MPFR speedup figures come from the paper abstract, seen only in search summaries because arXiv and the SPCL host were blocked. FPGA board versus a whole 36-core CPU node, not an equal-silicon comparison; CPU model, compiler and MPFR version are not in the README. Last commit 2022-05-17, more than 3 years old.

Fixed precision chosen at compile time (APFP_BITS, a multiple of 512 bits, 63-bit exponent, 1-bit sign), needs Xilinx Vitis HLS and an XRT-enabled FPGA card, results exposed only through matrix-multiply kernels, not a general library.

## Maintenance

Abandoned research artifact (last commit 2022-05-17, three PRs open since early 2022) with no license file, so treat it as reference code for study, not something to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README repeats the peer-reviewed FCCM'22 result (2.0 GMAC/s of 512-bit GEMM on an Alveo U250, an order of magnitude above a 36-core dual-socket Xeon node, 375x CPU cores); the repository only times the FPGA side (host/Microbenchmark.cpp, host/TestMatrixMultiplication.cpp) and uses MPFR as an untimed correctness reference, and the CPU model, compiler and flags of the baseline are not in the repo, so not A.
- **Verifier notes:** README numbers match the record; the paper (arXiv 2204.06256) was unreachable (arxiv.org, ar5iv, spcl.inf.ethz.ch, eupilot.eu blocked), so the MPFR ratios stay labelled as abstract-summary figures. Tier B on the strength of the FCCM'22 peer review.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/README.md>
  - <https://github.com/spcl/apfp>
  - <https://github.com/spcl/apfp/commits/main>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/host/Microbenchmark.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/host/TestMatrixMultiplication.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/host/MatrixMultiplicationReference.cpp>
- **Sources the enricher read:**
  - <https://github.com/spcl/apfp>
  - <https://github.com/spcl/apfp/commits/main>
  - <https://github.com/spcl/apfp/pulls>
  - <https://github.com/spcl/apfp/tree/main/interface>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/README.md>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/include/Config.h.in>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/include/DeviceTypes.h>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/include/PackedFloat.h>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/include/Karatsuba.h>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/include/PipelinedAdd.h>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/device/Karatsuba.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/device/ArithmeticOperations.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/interface/Apfp.h>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/interface/Apfp.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/host/Microbenchmark.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/host/TestMatrixMultiplication.cpp>
  - <https://raw.githubusercontent.com/spcl/apfp/HEAD/host/MatrixMultiplicationReference.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/spcl/apfp`) · [data/wave8/enrich/raw/github_com_spcl_apfp.json](../../../data/wave8/enrich/raw/github_com_spcl_apfp.json) (enrichment confidence 0.75)

</details>
