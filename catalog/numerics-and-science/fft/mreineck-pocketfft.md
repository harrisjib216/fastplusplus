# PocketFFT (C++ branch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++11 FFT (multi-D, any length, DCT/DST) behind NumPy and SciPy; about 4.5x faster than KissFFT on 3D transforms.

| | |
|---|---|
| **Beats** | KissFFT |
| **Claimed result** | 3D R2C 256^3: PocketFFT AVX 97 ms vs KissFFT 436 ms (4.5x, derived from page data); 416x256x416: 311 ms vs 2078 ms; 3D C2C 256^3: 264 ms vs 785 ms; also 'as fast as FFTW3' for AVX R2C (97 ms vs fftw3 meas. 98 ms) |
| **Workload** | 3D real-to-complex FFT, 256x256x256 single precision, plus 1D/2D complex FFTs, in a third-party shootout |
| **Metric** | throughput |
| **Hardware** | Intel i7-5600U, 4 threads @ 3200 MHz, L1 32K L2 256K L3 4096K |
| **Compiler and flags** | GCC 8 (g++-8) -O3 -Wall -Wextra -pedantic; pocketfft rows built with SSE or AVX (-march=native for pocketfft.o per Makefile) |
| **Adoption** | 148 stars; used inside NumPy and SciPy (per benchmark README) |
| **Last commit** | 2026-06-30 |
| **Links** | [repository](https://github.com/mreineck/pocketfft) · [benchmark](https://github.com/project-gemmi/benchmarking-fft) |

## Verdict

In project-gemmi's benchmarking-fft (GCC 8 -O3, i7-5600U, float, KissFFT scalar), the PocketFFT cpp branch with AVX did a 256^3 R2C in 97 ms vs KissFFT 436 ms (4.5x, derived) and 416x256x416 in 311 ms vs 2078 ms, matching FFTW measured from Ubuntu binaries (98 ms). The 3D C2C 256^3 run (SSE) took 264 ms vs KissFFT 785 ms but FFTW measured 162 ms.

## Use it when

- 2D/3D real or complex FFTs on strided or non-contiguous arrays, e.g. crystallography grids or image volumes
- Arbitrary lengths, including large primes, where FFTW's GPL or KissFFT's speed is a problem
- Workloads with many different sizes, where FFTW's plan time dominates (very fast setup)
- Projects that want one BSD header with DCT/DST and float/double/long double support
- Matching NumPy/SciPy FFT results in C++ code

## Skip it when

- Single short 1D transforms: the 1D path is not vectorized (4009 ns vs FFTW 588 ns and pffft 1255 ns at n=512 complex in gemmi's run, though that row used the older C version)
- Peak 3D throughput on Intel: MKL 2019 measured 61 ms vs 97 ms for 256^3 R2C
- Compilers other than GCC/Clang &gt;= 5: MSVC and ICC get no SIMD (vectorization is gated on GCC/Clang)
- Windows multithreading: it uses pthreads (open issue #2 asks for a Windows pool)
- You need versioned releases: none are tagged (open issue #24)

## How it is fast

The core is a heavily reworked FFTPACK with radix codelets for 2, 3, 4, 5, 7, 8 and 11 (complex) and 2, 3, 4, 5 (real), plus Bluestein's algorithm so large-prime lengths stay O(N log N). For multi-D or batched transforms it runs several 1D lines at once using GCC/Clang vector_size types (SSE2, AVX, AVX-512, NEON, VSX, RISC-V V), and it splits the work across an internal pthread thread pool. Twiddle factors take only about 2\*sqrt(n) sin/cos calls, so plan setup is cheap (1274 ns vs FFTW's 25610 ns at n=512 in the gemmi benchmark).

## Compared with alternatives

Pick PocketFFT over pffft and muFFT for multi-dimensional data, arbitrary lengths, double/long double, or DCT/DST. Pick pffft or muFFT for SIMD-accelerated short 1D transforms of 5-smooth or power-of-two sizes.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (pthreads for multithreading unless POCKETFFT_NO_MULTITHREADING) |
| **Minimum toolchain** | C++11; SIMD needs GCC &gt;= 5 or Clang &gt;= 5 (AppleClang &gt;= 9.1) |
| **Platforms** | any C++11 platform; SIMD on x86 SSE2/AVX/AVX-512, ARM NEON, POWER VSX, RISC-V V via compile-time flags such as -march=native |
| **Thread safety** | Free functions; the optional plan cache (POCKETFFT_CACHE_SIZE) and thread pool are mutex-protected; the nthreads argument sets parallelism for multi-D transforms |
| **Drop-in for the baseline** | no |

## Gotchas

- Strides are in bytes, not elements; r2c/c2r cannot be done in place
- Transforms are unnormalized: pass the scale via fct
- The plan cache is off by default (POCKETFFT_CACHE_SIZE=0); turn it on for repeated short 1D transforms, but it can use a lot of memory for large lengths
- Errors throw C++ exceptions (std::runtime_error, invalid_argument, bad_alloc); there is a reported aligned_alloc build failure on Android/Termux clang (issue #23)

## Known shortcomings

- GitHub repo is a fork of gitlab.mpcdf.mpg.de/mtr/pocketfft and the benchmark ran the gitlab cpp branch; 1D rows used the old C version (double, not vectorized); MKL is faster; FFTW from Ubuntu binaries.
- 1D transforms not vectorized; SIMD only with GCC or Clang 5+ (MSVC/ICC scalar); multithreading via pthreads (issue #2); no versioned releases (issue #24); Android/Termux clang build fails on aligned_alloc (issue #23).

## Caveats and trade-offs

Benchmark run by a user of the library (gemmi author) on the gitlab mpcdf cpp branch, which this GitHub repo mirrors. 1D rows used the older C version (double precision, not vectorized) and are slower than FFTW. FFTW came from Ubuntu 18.04 binaries, not self-built. MKL 2019 is faster (61 ms vs 97 ms R2C 256^3). Old CPU and compiler. KissFFT rows are scalar builds. The repo README gives no numbers.

Vectorized only for multi-D or batched transforms via GCC/Clang vector_size; 1D not SIMD, so 1D C2C 512 (4009 ns) is far slower than FFTW with SIMD (588 ns). Very fast plan generation (1274 ns vs 25610 ns FFTW).

## Maintenance

Active (commits through mid-2026); this GitHub fork mirrors the canonical gitlab.mpcdf.mpg.de/mtr/pocketfft cpp branch; BSD-3-Clause single header, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** gemmi shootout code (3d.cpp, 3d-r.cpp, 2d.cpp, Makefile) is public with GCC 8 -O3 and i7-5600U stated; the 3D R2C/C2C pocketfft vs kissfft numbers match the page.
- **Verifier notes:** GitHub repo says it is a fork of the gitlab.mpcdf.mpg.de/mtr/pocketfft canonical repo, kept to ease contributions; the benchmark used the gitlab cpp branch. Commits page shows 2026-06-30.
- **Fields the verifier corrected:** `is_fork_of`, `last_commit`, `maintenance_status`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/project-gemmi/benchmarking-fft>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/Makefile>
  - <https://github.com/mreineck/pocketfft>
  - <https://github.com/mreineck/pocketfft/commits>
- **Sources the enricher read:**
  - <https://github.com/mreineck/pocketfft>
  - <https://raw.githubusercontent.com/mreineck/pocketfft/cpp/README.md>
  - <https://raw.githubusercontent.com/mreineck/pocketfft/cpp/pocketfft_hdronly.h>
  - <https://github.com/mreineck/pocketfft/issues>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mreineck/pocketfft`) · [data/wave8/enrich/raw/github_com_mreineck_pocketfft.json](../../../data/wave8/enrich/raw/github_com_mreineck_pocketfft.json) (enrichment confidence 0.85)

</details>
