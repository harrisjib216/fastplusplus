# AppleSiliconFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Metal Shading Language, Swift` · `MIT` · 🟢 active

> Research Metal GPU and SME2 FFT kernels for Apple Silicon; M1 GPU N=4096 batch beats one-thread vDSP by 29%.

| | |
|---|---|
| **Beats** | Apple vDSP/Accelerate FFT (CPU) |
| **Claimed result** | Apple M1, N=4096 batch=256 (README): radix-8 Stockham 138.45 GFLOPS (1.78 us/FFT) vs vDSP 107.0 GFLOPS (2.29 us/FFT), +29%; in-place Cooley-Tukey with simdgroup_matrix 128 GFLOPS (+20%); radix-4 Stockham 113.6 GFLOPS (+6%). Apple M6 (m6/README.md): one-pass N=8192/16384 kernels 2.2x / 1.85x faster than MPSGraph (4.4x with FP16 storage); per m6/results/stage3_onepass.stdout this holds at DRAM-resident batches (N=8192 batch 2048: 604.4 vs 257.4 GF hot; N=16384 batch 1024: 547.2 vs 296.0 GF cold), while at L2-resident N=16384 MPSGraph is faster (805.2 vs 220.4 GF). CPU SME2 radix-8 FFT 'up to 5.3x' vDSP is the column-FFT case (m6/results/stage5_col.stdout, N=512 x W=256 matrix, 1 thread: SME 263.4 GF vs vDSP transpose+fftm+transpose 49.6 GF); for contiguous batched FFTs (stage5_fft.stdout) SME-CG beats vDSP_fft by 1.21x to 3.52x, but only 0.51x to 1.76x once packing into the SME layout is counted, i.e. slower than vDSP at N&gt;=512. |
| **Workload** | Batched single-precision complex FFT on the Apple M1 GPU (Metal kernels), N=4096, batch=256, GFLOPS vs vDSP on the same machine. |
| **Metric** | throughput |
| **Hardware** | Apple M1 (main README; GPU core count and macOS version not stated); Apple M6, macOS 27.0 (m6/README.md; logs dated 2026-09-26) |
| **Compiler and flags** | M1: xcrun metal + metallib; host swiftc -O -framework Metal -framework Accelerate (Xcode and macOS versions not stated). M6: swift build -c release for the M6Bench harness; SME2 C kernels clang -O3 -mcpu=apple-m4 (build line recorded in each m6/results log header). |
| **Adoption** | 6 stars, 1 fork, 5 commits |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/aminems/AppleSiliconFFT) · [benchmark](https://github.com/aminems/AppleSiliconFFT) |

## Verdict

On an Apple M1 (macOS and Xcode versions not stated), the radix-8 Metal kernel computed N=4096 complex FP32 FFTs in batches of 256 at a median 1.78 us per FFT of GPU-only time (138.45 GFLOPS by 5N log2 N), against 2.29 us (107 GF) for single-threaded vDSP_fft_zop timed by wall clock, so +29% is GPU vs one CPU core. On an Apple M6 (macOS 27.0, logs dated 2026-09-26), one-pass kernels beat MPSGraph about 2.3x at DRAM-resident N=8192 and lose about 3.7x at L2-resident N=16384. The SME2 FFT is 1.21-3.52x vDSP on contiguous batches before packing, 0.51-1.76x after, and 5.3x on N=512 x 256 column FFTs against vDSP transpose+fftm+transpose.

## Use it when

- As a reference when writing your own Metal FFT for one fixed power-of-two size (N=4096 complex FP32), where a register-resident single-threadgroup design matters
- Large DRAM-resident batches of N=8192 or 16384 complex FP32 on an M-series GPU: on M6 the one-pass N=8192 kernel ran at 604 GF vs 257 GF for MPSGraph (batch 2048, hot)
- Column FFTs of a row-major split-complex matrix on an M4-or-later CPU (SAR azimuth pass, second pass of a 2-D FFT): the SME2 column kernel needs no transpose and logged 2.7-5.3x over vDSP transpose+fftm+transpose at N up to 4096
- Matched-filter style pipelines (FFT, pointwise multiply, IFFT) where fusing into one dispatch removes device-memory round trips: the fused SAR pipeline was 22x faster than the author's own unfused version on M1

## Skip it when

- Anything that needs a library: there is no packaged API, the GPU kernels are FP32 and powers of two only (the N=4096 kernels are hard-coded, multi-size covers 256-16384), and the SME2 path accepts only N = 64, 512, 4096 or 32768
- Comparisons against a multithreaded CPU: the +29% is GPU-only time against a single-threaded vDSP_fft_zop loop timed by wall clock
- L2-resident batches at N=16384 on M6: MPSGraph (805 GF) and the repo's own two-pass four-step kernel (708 GF) beat the one-pass kernel (220 GF)
- Contiguous batched FFTs on the CPU with data already in vDSP's split-complex layout: once packing into the SME layout is counted, SME2 runs at 0.51-0.89x of vDSP for N &gt;= 512
- Non-Apple hardware, or Apple GPUs before M1: Metal and Apple Silicon only, macOS 13+; the SME2 code needs an M4 or later

## How it is fast

Each GPU threadgroup holds a whole N=4096 transform in registers and uses the 32 KiB of threadgroup memory only as an exchange buffer between passes. Four radix-8 passes use a split-radix 8-point butterfly with twiddles from sincos, and Stockham autosort keeps device-memory access coalesced. On M6, one-pass N=8192/16384 kernels keep the transform on chip, so large batches make a single trip through DRAM and run near the 150 GB/s limit. The SME2 path writes each radix-8 butterfly, twiddles included, as a 16x16 real matrix applied with FMOPA outer products to 16 FFTs at once in a ZA tile (constant-geometry Pease DIF, batch-minor layout).

## Compared with alternatives

VkFFT is the catalogued choice for a real GPU FFT library on Apple hardware (it has a Metal backend and arbitrary sizes). Pick AppleSiliconFFT only as reference kernels for Apple-specific tricks: register-resident one-pass N=8192/16384 kernels, fused SAR pipelines, or SME2 column FFTs on M4+ CPUs. For portable CPU FFTs, Admiral or PocketFFT apply instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Metal and Accelerate frameworks; Xcode Command Line Tools (swiftc, xcrun metal, clang); M6 harness: Swift 5.9+; plots: Python 3 with pandas and matplotlib (MLX 0.29.3 and NumPy for the landscape script) |
| **Minimum toolchain** | macOS 13.0+ and Swift via Xcode CLT for the M1 code; Swift 5.9+ and clang -O3 -mcpu=apple-m4 for the M6/SME2 code; GPU matrix-unit modes need macOS 26+ and an M5-class GPU |
| **Platforms** | Apple Silicon only (M1 or later for the GPU kernels, M4 or later for SME2) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The M1 host fft_host.swift compiles Metal source at run time and looks for fft_4096_mma.metal, which is not in the repo. The 138 GFLOPS kernel is src/fft_4096_radix8.metal (kernel function fft_4096_mma), so you have to copy or rename it; the README's xcrun metal/metallib steps are not what the host loads
- The headline kernel is labeled inconsistently. Its header comment says stages 1-3 use simdgroup_matrix MMA, but all four passes call the scalar radix8_butterfly, and the README calls it both 'Radix-8 Stockham' and 'split-radix DIT'. The simdgroup_matrix kernel is the 128 GFLOPS fft_4096_ct_mma.metal
- The hosts enable Metal fastMathEnabled, and the pass criterion is an L2 relative error below 1e-5 against vDSP
- sme_fft_execute leaves output in base-8 digit-reversed order and batch-minor blocks of 16 FFTs (use sme_fft_unpack). Build with -mcpu=apple-m4, not -march=armv9, or the program dies with SIGILL. On M6, hot and cold runs differ by up to 3.7x

## Known shortcomings

- M1 +29% is the whole GPU against a single-threaded vDSP loop; the M6 '5.3x over vDSP' applies only to column FFTs of a matrix, and on contiguous batches the SME2 path (counting packing) is slower than vDSP from N=512 up; the one-pass kernels beat MPSGraph only on DRAM-resident batches (MPSGraph is 3.7x faster at L2-resident N=16384).
- Claim not reproducible as shipped: fft_host.swift loads fft_4096_mma.metal, which is not in the repo; the 138 GFLOPS kernel (src/fft_4096_radix8.metal, function fft_4096_mma) claims simdgroup_matrix MMA in a comment but all four passes run the scalar radix8_butterfly, and the README calls it both 'Stockham' and 'split-radix DIT'; hosts use Metal fastMath; SME2 'up to 5.3x' compares against vDSP transpose+fftm+transpose (11.3x against strided fftm).

## Caveats and trade-offs

The M1 +29% compares the whole GPU against a single CPU core: GPU kernels are timed from the command buffer's gpuStartTime to gpuEndTime (GPU execution only, dispatch overhead excluded), while the vDSP baseline (benchmarks/Sources/vdsp_baseline_bench.swift) is one thread looping vDSP_fft_zop (radix-2 setup, split complex) and timing the wall clock; a multithreaded vDSP baseline was not measured. The M1 headline is for one size (N=4096, batch 256); the multi-size table (N=256 to 16384, batch 64) lists GFLOPS without vDSP columns. On M6 the one-pass kernels beat MPSGraph only at DRAM-resident batches (MPSGraph is 3.7x faster at L2-resident N=16384, derived from page data), and the SME2 'up to 5.3x' figure is for column FFTs of a matrix; for contiguous batches with packing counted the SME path is slower than vDSP at N&gt;=512. Hot and cold runs differ by up to 3.7x per the m6 README. The M6 hardware and macOS 27.0 may be hard for a verifier to reproduce. Research code (Metal kernels, Swift host harnesses, C SME2 kernels), not a packaged C++ library. Results come from the author's own preprints (arXiv 2603.27569 for the M1 paper and 2609.32237 for the M6 paper per search results), not peer reviewed as far as could be checked. Baseline is Apple-specific (vDSP, MPSGraph), not FFTW, MKL or KissFFT. [retier] Host loads a missing fft_4096_mma.metal; the headline kernel runs scalar radix-8 butterflies despite its MMA comment; Metal fastMath on.

GPU-only Metal kernels, power-of-two sizes 256 to 16384 (four-step for larger), single precision; N=4096 batch workload; Apple Silicon only.

## Maintenance

Active as of 2026-09-26, with 5 commits and 6 stars. It is MIT-licensed research code tied to the author's preprints and is easy to copy kernels from, but it has no API, tests beyond the validation hosts, or packaging.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now C.
- **Tier reason:** Code for both baselines is public: M1 GPU kernels with src/fft_host.swift and the vDSP baseline in benchmarks/Sources/vdsp_baseline_bench.swift (swiftc -O, Apple M1), and for M6 the M6Bench harness plus m6/benchmarks/micro/sme/sme_stage5.c built with clang -O3 -mcpu=apple-m4 on an Apple M6 under macOS 27.0, with raw logs in m6/results whose headers record date, OS and build line. Toolchain versions are not stated for the M1 run, which is the weaker half.
- **Retiered** A to C: Enrichment found the harness not reproducible as shipped: the host loads fft_4096_mma.metal, which is not in the repo, and the kernel that produces the headline is mis-described (comment claims simdgroup MMA, code runs scalar butterflies). Public code that does not run as published does not meet tier A.
- **Verifier notes:** README numbers match. The vDSP baseline is a single-threaded loop and GPU time is GPU-only, so the +29% is GPU vs one CPU core; the SME2 5.3x is the matrix-column case and the SME path loses to vDSP on contiguous batches once packing is included. arxiv.org is blocked here, so the arXiv IDs come from a WebSearch result only.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/aminems/AppleSiliconFFT>
  - <https://github.com/aminems/AppleSiliconFFT/commits/main>
  - <https://github.com/aminems/AppleSiliconFFT/tree/main/m6/results>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/README.md>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/src/fft_host.swift>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/benchmarks/Sources/vdsp_baseline_bench.swift>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/results/stage5_fft.stdout>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/results/stage5_col.stdout>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/results/stage3_onepass.stdout>
- **Sources the enricher read:**
  - <https://github.com/aminems/AppleSiliconFFT>
  - <https://github.com/aminems/AppleSiliconFFT/tree/main/src>
  - <https://github.com/aminems/AppleSiliconFFT/tree/main/m6/src/metal>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/README.md>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/src/fft_4096_radix8.metal>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/src/fft_host.swift>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/src/fft_multisize_host.swift>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/benchmarks/Sources/vdsp_baseline_bench.swift>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/src/cpu/sme_fft.h>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/results/stage5_fft.stdout>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/results/stage5_col.stdout>
  - <https://raw.githubusercontent.com/aminems/AppleSiliconFFT/HEAD/m6/results/stage3_onepass.stdout>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/aminems/applesiliconfft`) · [data/wave8/enrich/raw/github_com_aminems_applesiliconfft.json](../../../data/wave8/enrich/raw/github_com_aminems_applesiliconfft.json) (enrichment confidence 0.75)

</details>
