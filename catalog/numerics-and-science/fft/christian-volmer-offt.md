# OFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Scalar, BSL-licensed C++11 mixed-radix FFT for arbitrary lengths; beats FFTW_ESTIMATE at some awkward sizes, loses elsewhere.

| | |
|---|---|
| **Beats** | FFTW 3.3.5 (FFTW_ESTIMATE, with and without SIMD) and Intel oneMKL |
| **Claimed result** | Author: for arbitrary sizes OFFT is often faster than FFTW, even the SIMD version. From the table (ns per n ln n): OFFT beats FFTW_ESTIMATE with SIMD at 10 of 30 non-power-of-two lengths (e.g. 1025: 6.7 vs 8.0; 4097: 6.0 vs 7.4; 262145: 9.0 vs 11.6; 16777217: 8.7 vs 12.3, i.e. 1.41x derived from page data), ties at 4194305, and loses at the other 19. It beats single-thread MKL at 12 of 30 non-power-of-two lengths (e.g. 32769: 7.2 vs 14.4; 4194305: 9.7 vs 14.7) and 2-thread MKL at 3 (2047, 65537, 131073). It is slower than FFTW with SIMD and than MKL at every power of two and ten (1024: 2.1 vs 0.5). |
| **Workload** | Complex FFT at powers of two (1024 to 2^24), powers of ten and 30 non-power-of-two lengths (1023 to 16777217); numbers are nanoseconds per n\*ln(n), single table per size. |
| **Metric** | latency |
| **Hardware** | Intel i5-2450M 2.5 GHz laptop, SSE4 only, Windows 10 |
| **Compiler and flags** | GCC 12.2.0 (MSYS2 Rev11) on Windows; optimization flags not stated (CMakeLists.txt sets only -Wall -Wextra -Wpedantic -std=c++11; build type not given). FFTW 3.3.5 official Windows DLLs; MKL vendor binaries. |
| **Adoption** | 3 stars |
| **Last commit** | 2024-05-12 |
| **Links** | [repository](https://github.com/christian-volmer/OFFT) · [benchmark](https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/doc/OfftSpeedComparison.md) |

## Verdict

First-party table (doc/OfftSpeedComparison.md, v0.3.0): MSYS2 GCC 12.2.0 on Windows 10, Intel i5-2450M (SSE4 only), against the official FFTW 3.3.5 Windows DLLs with FFTW_ESTIMATE (with and without SIMD) and oneMKL limited to 1 or 2 threads, in ns per n ln n. OFFT wins 10 of 30 non-power-of-two sizes against SIMD FFTW (best 16777217: 8.7 vs 12.3, 1.41x) and 12 of 30 against 1-core MKL, but loses at every power of two and ten; optimization flags are not stated, and the FFTW/MKL comparison harness is not in the repo (examples/benchmark links only OFFT).

## Use it when

- Complex FFTs at awkward lengths with large prime factors (e.g. 1025, 4097, 16385, 262145, 16777217) where you cannot afford FFTW_MEASURE planning: OFFT beat FFTW_ESTIMATE with SIMD at 10 of 30 such sizes on the author's machine.
- Projects that need a permissive (Boost Software License), dependency-free FFT and cannot ship FFTW under GPL or install Intel MKL.
- Portable scalar code for any C++11 platform, including targets without SSE/AVX, where FFTW's SIMD advantage disappears (OFFT beat scalar FFTW_ESTIMATE at 25 of 30 awkward sizes, derived from page data).
- Multi-dimensional or strided transforms on interleaved data such as stereo audio or RGB planes, with a choice of DFT sign and scaling convention.

## Skip it when

- Powers of two or ten: SIMD FFTW_ESTIMATE and 1-core MKL are about 1.4-4.2x faster on the author's table (derived from page data; 1024: 2.1 vs 0.5 ns per n ln n for both).
- Throughput on modern AVX/AVX-512 hardware: OFFT has no SIMD, and the benchmark machine was an SSE4-only laptop the author calls 'pretty ancient'; he expects the SIMD gap to be larger on newer CPUs.
- Real-valued signals, in-place transforms or split real/imaginary arrays: none have a public API yet (README known limitations).
- Sizes with a prime factor that does not fit in 32 bits fail, even on 64-bit targets.
- When you need a stable API or active maintenance: version 0.3.0 (June 2023), the API may change between minor versions, 3 stars, last commit 2024-05-12 (.clang-format only).

## How it is fast

It runs an out-of-place, decimation-in-time mixed-radix Cooley-Tukey driver over code-generated straight-line kernels for factors up to 32. Primes 3-31 use Rader's algorithm with Winograd cyclic convolutions, composites such as 6, 10, 12 and 15 use the Good-Thomas prime-factor decomposition, and 8, 16 and 32 use split-radix. Larger prime factors go through a general Rader algorithm with an FFT-based cyclic convolution, so run time stays O(n log n) for any n, and twiddles are precomputed in compact storage. There is no SIMD; its wins come at lengths with large or awkward prime factors, where FFTW_ESTIMATE plans are weak.

## Compared with alternatives

Pick OFFT over FFTW when GPL or MKL licensing is a blocker and your sizes are prime-heavy. For speed on regular sizes, prefer SIMD libraries such as PocketFFT (C++ branch), pocketfft-tuned or VectorFFT; OFFT has no head-to-head numbers against them.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 (target_compile_features cxx_std_11; GCC builds force -std=c++11), CMake 3.10; Visual Studio 2017 solution, VS2013 via toolset v120; benchmarked with MSYS2 GCC 12.2.0 |
| **Platforms** | any (platform-independent scalar C++11; no SIMD paths) |
| **Thread safety** | Use one Fourier object per thread: Transform() and InverseTransform() are const but lazily allocate and write a mutable scratch buffer (mTemp in fourier_base.cpp), so concurrent calls on one object race. Each object owns its own storage; no other thread-safety notes are documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default convention FourierParameters{1,1} computes the forward transform with e^(+2 pi j ik/N), the opposite sign to FFTW's forward transform; pass offt::FourierParameters::FFTW ({1,-1}) to match FFTW. Inverse is scaled by 1/N by default.
- Source and destination must differ (no in-place); data must be std::complex&lt;float/double&gt;, interleaved.
- Thread-safety trap: the transform methods are const yet mutate internal scratch memory (see thread_safety); ReleaseTemp() frees it and the next call reallocates.
- The constructor throws (std::invalid_argument for a bad sign parameter; the element-count product throws on overflow), so wrap construction if your code is exception-free.

## Known shortcomings

- Beats 1-core MKL at only 12 of 30 awkward sizes; optimization flags not stated.
- Not reproducible: the FFTW/MKL comparison code is not in the repo (examples/benchmark links only OFFT); forward transform uses the opposite sign to FFTW by default; Transform() is const but writes a shared scratch buffer, so concurrent calls on one object race.

## Caveats and trade-offs

Mixed result that the author's wording overstates: slower than FFTW_ESTIMATE with SIMD at powers of two and ten and at 19 of 30 non-power-of-two sizes (one tie); slower than MKL at all regular sizes, but faster than single-thread MKL at 12 awkward sizes. FFTW_MEASURE was deliberately not used. Old CPU (SSE4 only), no SIMD in OFFT, optimization flags not stated, FFTW 3.3.5 Windows binaries. The author says the numbers are noisy (background processes, thermal clock changes).

C++11 header-style library for arbitrary-length transforms, no SIMD yet, code-generated kernels, keeps code size small.

## Maintenance

Stale one-person project (v0.3.0 June 2023, last commit May 2024, 3 stars, CI self-test on GitHub Actions) under the Boost Software License; small enough to vendor, but treat the API as unstable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/OfftSpeedComparison.md is a first-party table against FFTW 3.3.5 (FFTW_ESTIMATE, with and without SIMD) and oneMKL, with compiler (MSYS2 GCC 12.2.0) and CPU (i5-2450M). Optimization flags are not stated, and CMakeLists.txt sets only warnings and -std=c++11, so C.
- **Verifier notes:** Win counts recomputed from the table; the record's 'slower than MKL' was too broad (OFFT beats 1-core MKL at 12 of 30 awkward sizes). BSL-1.0, 3 stars, last commit 2024-05-12 (main), stale, all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** Beats scalar FFTW_ESTIMATE at 25 of 30 awkward sizes (derived from page data).
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/doc/OfftSpeedComparison.md>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/CMakeLists.txt>
  - <https://github.com/christian-volmer/OFFT>
  - <https://github.com/christian-volmer/OFFT/commits>
- **Sources the enricher read:**
  - <https://github.com/christian-volmer/OFFT>
  - <https://github.com/christian-volmer/OFFT/commits/main>
  - <https://github.com/christian-volmer/OFFT/tree/main/offt>
  - <https://github.com/christian-volmer/OFFT/tree/main/examples/benchmark>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/doc/OfftSpeedComparison.md>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/LICENSE_1_0.txt>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/CMakeLists.txt>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/include/offt.h>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/include/offt/backend/fourier_base.h>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/include/offt/fourier_parameters.h>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/include/offt/compat.h>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/src/backend/fourier_base.cpp>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/offt/src/backend/storage.cpp>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/examples/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/examples/benchmark/self_test.cpp>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/examples/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/christian-volmer/OFFT/HEAD/examples/benchmark/transform_test.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/christian-volmer/offt`) · [data/wave8/enrich/raw/github_com_christian_volmer_offt.json](../../../data/wave8/enrich/raw/github_com_christian_volmer_offt.json) (enrichment confidence 0.8)

</details>
