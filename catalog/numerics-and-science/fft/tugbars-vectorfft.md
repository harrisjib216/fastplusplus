# VectorFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Double-precision x86 AVX2/AVX-512 FFT library in C, with generated codelets and a wisdom planner; median 1.29x Intel MKL on 1D c2c.

| | |
|---|---|
| **Beats** | Intel oneMKL 2025.3 FFT (DFTI, sequential) |
| **Claimed result** | 1D: 1.29x median over MKL across N=2..4,096 (89% of 4,095 lengths at/above parity; best 7.04x at N=89; powers of two 1.13x median, 75% at/above parity); 2D 1.34x median over 159 pow2 planes (94% at/above parity); 3D 1.55x median over 1,288 pow2 volumes (98% at/above parity) (README) |
| **Workload** | 1D complex-to-complex FP64 interleaved out-of-place, every length N=2..4096, single thread; also 2D/3D power-of-two planes/volumes |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-14900KF (P-core, AVX2), DDR5 |
| **Compiler and flags** | GCC 15.2, -O3 -mavx2 -mfma -march=native -mno-avx512f (gauntlet/build.py, CMakeLists.txt) |
| **Adoption** | 5 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/Tugbars/VectorFFT) · [benchmark](https://github.com/Tugbars/VectorFFT) |

## Verdict

The author's gauntlet harness (public code and raw CSVs) on an Intel Core i9-14900KF P-core with AVX2 and GCC 15.2 at -O3 -march=native -mno-avx512f timed single-thread out-of-place interleaved FP64 c2c at every N from 2 to 4,096 against oneMKL 2025.3 sequential DFTI. It reports a 1.29x median speedup (89% of lengths at or above parity), 1.34x over 159 power-of-two 2D planes and 1.55x over 1,288 3D volumes, each ratio taking the worse of two engine orders. FFTW 3.3.10 (FFTW_MEASURE, vcpkg DLL) comparisons cover only real r2c/c2r and r2r transforms, with medians of 1.15-1.23x on powers of two and a few small-N losses.

## Use it when

- Many FP64 complex transforms of modest length (N up to a few thousand) on AVX2 or AVX-512 x86, where MKL's sequential DFTI is the incumbent
- Awkward lengths (primes, large-prime composites, odd smooth sizes), where the README reports median 1.18x over MKL on primes and up to 7.04x at N=89
- Small 2D and 3D power-of-two grids (median 4.5x over MKL below 256 or 4,096 points) and batched DCT/DST work, where its tables show 2-4x over FFTW
- Projects that need an MIT-licensed alternative to MKL or GPL FFTW and can recalibrate wisdom on their target CPU

## Skip it when

- Single-precision, ARM/Apple Silicon or other non-x86 targets: it is FP64 only and ships only AVX2 and AVX-512 codelet trees
- Mid-size powers of two (32..512): it is at or slightly below MKL there (0.94-1.03x), and the power-of-two median lead is only 1.13x
- Workloads that need full double accuracy on every length: 33 large-odd-radix lengths exceed the README's 10e-16 error line and there is no accuracy mode
- Production code that needs a mature, packaged library: 5 stars, one author, very new, no install target; the root CMake builds only a codelet static lib and the benchmark tools
- Linux or POSIX-first deployments where you want tested comparisons: the harness targets Windows (its FFTW binding says the POSIX path is untested)

## How it is fast

Kernels are straight-line, register-allocated C codelets emitted per instruction set by the project's own DAG FFT compiler (OCaml-based, per the repo page), including Winograd-style odd radices, large conjugate-pair radix stages up to 47, Rader and Bluestein for primes, and a cache-tiled four-step path for large powers of two. The planner races every candidate route on the host CPU and keeps the winner as wisdom, so the first create of a size measures (milliseconds to seconds) and later creates replay the banked plan. Some odd composite lengths derive most twiddle factors from one loaded value instead of loading them all, trading a small accuracy loss for speed.

## Compared with alternatives

Pick VectorFFT over KFR, PocketFFT or PFFFT when the workload is FP64 on modern x86, an MIT license matters, and you can benchmark and recalibrate on your own CPU; pick KFR or PocketFFT for portability (ARM, float), maturity or a C++ API, and VkFFT for GPUs.

## Integration

| | |
|---|---|
| **Form** | source-drop (header-only core in src/core plus src/core/vfft.c, linked with a static lib of generated codelets; no install or package target) |
| **Dependencies** | none at runtime beyond libm and the platform thread library; MKL and FFTW only for the optional benchmark comparators |
| **Minimum toolchain** | C11; CMake 3.16; GCC, Clang, Intel ICX or MSVC-style front ends (README benchmarks used GCC 15.2); CPU with AVX2+FMA or AVX-512F/DQ |
| **Platforms** | x86-64 only (AVX2+FMA default build, AVX-512 optional); ISA fixed at build time, with no runtime dispatch; developed and benchmarked on Windows, Linux builds supported by CMake |
| **Thread safety** | vfft_execute performs no allocation and is safe to call concurrently on different plans; vfft_set_num_threads is process-global and must not run concurrently with plan creation or execution |
| **Drop-in for the baseline** | no |

## Gotchas

- vfft_set_num_threads(n&gt;1) pins the calling thread to core 0 and the workers to the following cores; reset your own affinity afterwards
- The default layout is SPLIT, and for SPLIT at 2D and above the default output order is SCRAMBLED (only a roundtrip through the same plan decodes it); request VFFT_ORDER_NATURAL or the interleaved layout explicitly
- Errors are printed, not returned: vfft_create returns NULL, and vfft_execute with a pointer signature that does not match the plan computes nothing and returns void
- Shipped wisdom was calibrated on an i9-14900KF; on other CPUs the first create of each size races candidates unless you recalibrate. The build suppresses implicit-function-declaration and incompatible-pointer-type warnings (-fpermissive), and examples/CMakeLists.txt notes an intermittent MinGW GCC segfault in the quickstart demo

## Known shortcomings

- Single machine (first-party, reproducible); on powers of two only 1.13x median over MKL with 25% of cases below parity; some odd lengths trade accuracy for speed (33 lengths error &gt;1e-16), no accuracy mode; FFTW 3.3.10 comparison only for real transforms, loses small cases (N=15 at 0.70x); 5 stars.
- FFTW comparisons cover only r2c/c2r/r2r, not the headline c2c; 33 lengths trade accuracy for speed.
- vfft_set_num_threads pins the calling thread to core 0; build flags suppress implicit-function-declaration and incompatible-pointer-type warnings (-fpermissive).
- Packaging gaps: no install target; examples/CMakeLists.txt links a vfft target defined only by an orphaned src/CMakeLists.txt; quickstart demo segfaults intermittently under MinGW GCC; FFTW binding targets Windows (POSIX path untested).

## Caveats and trade-offs

First-party benchmark (fully reproducible, but run by the author on one machine; harness hints at a Windows/vcpkg setup). Powers of two only 1.13x median over MKL with 25% of pow2 cells below parity. Speed on some large odd lengths comes from derived twiddles that trade accuracy (33 lengths have error above 1e-16; README says no accuracy mode is offered). docs/performance/v1_0_results.md has FFTW 3.3.10 comparisons for real r2c/c2r (mostly faster, some small-N losses, e.g. N=15 at 0.70x), not for the headline c2c table. Very new repo, 5 stars.

x86 only (AVX2/AVX-512); FFT kernels generated by an OCaml DAG compiler; pure C API with wisdom planner

## Maintenance

Very active (2,449 commits, results dated up to 2026-10-01) but a 5-star single-author project with no tagged release; MIT-licensed, so it can be vendored if you also take on the build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C-&gt;A: benchmark code is public (gauntlet/bench_1d_vs_mkl.c driven by gauntlet/gauntlet.py, raw csv records in gauntlet/results/gauntlet_2_4096_2026-09-23/), compiler GCC 15.2 and CPU i9-14900KF stated in README, flags public in gauntlet/build.py and CMakeLists.txt (-O3 -mavx2 -mfma -march=native -mno-avx512f).
- **Verifier notes:** README numbers match exactly. Metadata confirmed: MIT, not a fork/archived, last commit 2026-10-01, 5 stars. Record as shortcoming: accuracy trade on some odd lengths, and pow2 lead over MKL is thin.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** Mid-size powers of two (32-512) run 0.94-1.03x MKL (enrichment reading of the repo's results).
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/gauntlet/README.md>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/gauntlet/build.py>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/docs/performance/v1_0_results.md>
  - <https://github.com/Tugbars/VectorFFT>
  - <https://github.com/Tugbars/VectorFFT/commits>
- **Sources the enricher read:**
  - <https://github.com/Tugbars/VectorFFT>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/include/vfft.h>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/docs/performance/v1_0_results.md>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/gauntlet/README.md>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/gauntlet/ref_fftw.h>
  - <https://github.com/Tugbars/VectorFFT/tree/main/examples>
  - <https://raw.githubusercontent.com/Tugbars/VectorFFT/HEAD/examples/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tugbars/vectorfft`) · [data/wave8/enrich/raw/github_com_tugbars_vectorfft.json](../../../data/wave8/enrich/raw/github_com_tugbars_vectorfft.json) (enrichment confidence 0.8)

</details>
